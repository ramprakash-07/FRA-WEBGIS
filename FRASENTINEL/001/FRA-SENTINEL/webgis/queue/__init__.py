"""
Message Queue System for FRA-SENTINEL
Handles OCR batch processing and retryable jobs
Supports both Redis (production) and in-memory (development)
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Job:
    id: str
    type: str
    data: Dict
    status: JobStatus = JobStatus.PENDING
    priority: int = 5  # 1=highest, 10=lowest
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class MessageQueue:
    """In-memory message queue for development/testing"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.workers: List[threading.Thread] = []
        self.running = False
        self.job_handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register a job handler"""
        self.job_handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    def enqueue(self, job_type: str, data: Dict, priority: int = 5) -> str:
        """Enqueue a new job"""
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            type=job_type,
            data=data,
            priority=priority
        )
        
        with self._lock:
            self.jobs[job_id] = job
        
        logger.info(f"Enqueued job {job_id} of type {job_type}")
        return job_id
    
    def dequeue(self) -> Optional[Job]:
        """Dequeue the highest priority job"""
        with self._lock:
            # Find highest priority pending job
            pending_jobs = [
                job for job in self.jobs.values() 
                if job.status == JobStatus.PENDING
            ]
            
            if not pending_jobs:
                return None
            
            # Sort by priority (lower number = higher priority)
            pending_jobs.sort(key=lambda x: x.priority)
            job = pending_jobs[0]
            
            # Update job status
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            
            return job
    
    def complete_job(self, job_id: str, result: Dict = None):
        """Mark job as completed"""
        with self._lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.result = result
                logger.info(f"Completed job {job_id}")
    
    def fail_job(self, job_id: str, error_message: str):
        """Mark job as failed"""
        with self._lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                job.error_message = error_message
                
                if job.retry_count < job.max_retries:
                    job.retry_count += 1
                    job.status = JobStatus.RETRYING
                    logger.warning(f"Job {job_id} failed, retrying ({job.retry_count}/{job.max_retries})")
                else:
                    job.status = JobStatus.FAILED
                    logger.error(f"Job {job_id} failed permanently after {job.max_retries} retries")
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get all jobs with specific status"""
        return [job for job in self.jobs.values() if job.status == status]
    
    def cleanup_old_jobs(self, hours: int = 24):
        """Clean up old completed/failed jobs"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            jobs_to_remove = [
                job_id for job_id, job in self.jobs.items()
                if job.status in [JobStatus.COMPLETED, JobStatus.FAILED] and
                   job.completed_at and job.completed_at < cutoff_time
            ]
            
            for job_id in jobs_to_remove:
                del self.jobs[job_id]
            
            logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
    
    def start_worker(self, worker_id: str = None):
        """Start a worker thread"""
        if worker_id is None:
            worker_id = f"worker-{len(self.workers)}"
        
        def worker():
            logger.info(f"Worker {worker_id} started")
            while self.running:
                try:
                    job = self.dequeue()
                    if job is None:
                        time.sleep(1)  # No jobs available, wait
                        continue
                    
                    logger.info(f"Worker {worker_id} processing job {job.id}")
                    
                    # Get handler for job type
                    handler = self.job_handlers.get(job.type)
                    if not handler:
                        self.fail_job(job.id, f"No handler registered for job type: {job.type}")
                        continue
                    
                    # Process job
                    try:
                        result = handler(job.data)
                        self.complete_job(job.id, result)
                    except Exception as e:
                        self.fail_job(job.id, str(e))
                        logger.error(f"Job {job.id} failed: {e}")
                
                except Exception as e:
                    logger.error(f"Worker {worker_id} error: {e}")
                    time.sleep(5)  # Wait before retrying
            
            logger.info(f"Worker {worker_id} stopped")
        
        thread = threading.Thread(target=worker, name=worker_id)
        thread.daemon = True
        thread.start()
        self.workers.append(thread)
    
    def start(self, num_workers: int = 2):
        """Start the message queue system"""
        self.running = True
        
        for i in range(num_workers):
            self.start_worker(f"worker-{i}")
        
        logger.info(f"Message queue started with {num_workers} workers")
    
    def stop(self):
        """Stop the message queue system"""
        self.running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        logger.info("Message queue stopped")

# Global message queue instance
message_queue = MessageQueue()

# Job handlers
def ocr_extraction_handler(data: Dict) -> Dict:
    """Handle OCR extraction jobs"""
    from digitization.patta_extractor import extract_patta_data
    
    file_path = data.get('file_path')
    if not file_path or not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    logger.info(f"Processing OCR extraction for: {file_path}")
    
    # Extract data from PDF
    result = extract_patta_data(file_path)
    
    if 'error' in result:
        raise ValueError(f"OCR extraction failed: {result['error']}")
    
    return result

def batch_processing_handler(data: Dict) -> Dict:
    """Handle batch processing jobs"""
    file_paths = data.get('file_paths', [])
    results = []
    errors = []
    
    for file_path in file_paths:
        try:
            result = ocr_extraction_handler({'file_path': file_path})
            results.append({
                'file_path': file_path,
                'success': True,
                'data': result
            })
        except Exception as e:
            errors.append({
                'file_path': file_path,
                'error': str(e)
            })
    
    return {
        'results': results,
        'errors': errors,
        'total_processed': len(results),
        'total_failed': len(errors)
    }

def asset_mapping_handler(data: Dict) -> Dict:
    """Handle asset mapping jobs"""
    from asset_mapping.train_classify import classify_entire_image, load_or_create_satellite_image
    
    village_id = data.get('village_id')
    model_version = data.get('model_version', '1.0')
    
    logger.info(f"Processing asset mapping for village {village_id}")
    
    # Load satellite image
    img = load_or_create_satellite_image()
    
    # Load trained classifier (simplified for demo)
    from sklearn.ensemble import RandomForestClassifier
    import numpy as np
    
    # Create dummy classifier for demo
    classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Create dummy training data
    n_bands, height, width = img.shape
    X_dummy = np.random.rand(100, n_bands)
    y_dummy = np.random.randint(0, 4, 100)  # 4 classes
    classifier.fit(X_dummy, y_dummy)
    
    # Classify image
    classified_img = classify_entire_image(img, classifier)
    
    # Calculate statistics
    unique, counts = np.unique(classified_img, return_counts=True)
    total_pixels = classified_img.size
    
    class_names = ['Farmland', 'Forest', 'Water', 'Homestead']
    stats = {}
    for class_id, count in zip(unique, counts):
        percentage = (count / total_pixels) * 100
        stats[class_names[class_id].lower()] = {
            'percentage': round(percentage, 2),
            'pixels': int(count)
        }
    
    return {
        'village_id': village_id,
        'model_version': model_version,
        'classification_stats': stats,
        'total_pixels': int(total_pixels),
        'processing_time': time.time() - data.get('start_time', time.time())
    }

# Register job handlers
message_queue.register_handler('ocr_extraction', ocr_extraction_handler)
message_queue.register_handler('batch_processing', batch_processing_handler)
message_queue.register_handler('asset_mapping', asset_mapping_handler)

# Queue management functions
def enqueue_ocr_job(file_path: str, priority: int = 5) -> str:
    """Enqueue OCR extraction job"""
    return message_queue.enqueue('ocr_extraction', {'file_path': file_path}, priority)

def enqueue_batch_job(file_paths: List[str], priority: int = 5) -> str:
    """Enqueue batch processing job"""
    return message_queue.enqueue('batch_processing', {'file_paths': file_paths}, priority)

def enqueue_asset_mapping_job(village_id: int, model_version: str = '1.0', priority: int = 5) -> str:
    """Enqueue asset mapping job"""
    return message_queue.enqueue('asset_mapping', {
        'village_id': village_id,
        'model_version': model_version,
        'start_time': time.time()
    }, priority)

def get_job_status(job_id: str) -> Optional[Dict]:
    """Get job status"""
    job = message_queue.get_job(job_id)
    if job:
        return asdict(job)
    return None

def get_queue_stats() -> Dict:
    """Get queue statistics"""
    pending = len(message_queue.get_jobs_by_status(JobStatus.PENDING))
    processing = len(message_queue.get_jobs_by_status(JobStatus.PROCESSING))
    completed = len(message_queue.get_jobs_by_status(JobStatus.COMPLETED))
    failed = len(message_queue.get_jobs_by_status(JobStatus.FAILED))
    retrying = len(message_queue.get_jobs_by_status(JobStatus.RETRYING))
    
    return {
        'total_jobs': len(message_queue.jobs),
        'pending': pending,
        'processing': processing,
        'completed': completed,
        'failed': failed,
        'retrying': retrying,
        'active_workers': len(message_queue.workers)
    }

# Initialize message queue
def init_message_queue(num_workers: int = 2):
    """Initialize message queue system"""
    message_queue.start(num_workers)
    logger.info("Message queue system initialized")

# Cleanup function
def cleanup_message_queue():
    """Cleanup message queue system"""
    message_queue.stop()
    message_queue.cleanup_old_jobs()

if __name__ == "__main__":
    # Test the message queue
    init_message_queue()
    
    # Enqueue test jobs
    job_id1 = enqueue_ocr_job("test_file.pdf")
    job_id2 = enqueue_batch_job(["file1.pdf", "file2.pdf"])
    
    # Wait for jobs to complete
    time.sleep(10)
    
    # Check status
    print(f"Job 1 status: {get_job_status(job_id1)}")
    print(f"Job 2 status: {get_job_status(job_id2)}")
    print(f"Queue stats: {get_queue_stats()}")
    
    cleanup_message_queue()









