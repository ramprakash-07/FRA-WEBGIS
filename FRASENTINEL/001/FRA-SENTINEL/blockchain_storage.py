#!/usr/bin/env python3
"""
FRA-SENTINEL Blockchain Storage Module
Integrates blockchain functionality for document verification and storage
"""

import hashlib
import json
from datetime import datetime
from flask import request, jsonify
import os

class FRABlockchain:
    """Simple blockchain implementation for FRA document verification"""
    
    def __init__(self):
        self.documents = {}
        self.transactions = []
        self.block_number = 18456789
        self.network_name = "FRA-SENTINEL-NETWORK"
    
    def register_document(self, data):
        """Register a new FRA document on the blockchain"""
        try:
            # Create document hash
            doc_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            
            # Create transaction hash
            tx_hash = f"0x{hashlib.sha256(f'{doc_hash}_{datetime.now().timestamp()}'.encode()).hexdigest()[:40]}"
            
            # Store document
            self.documents[doc_hash] = {
                'hash': doc_hash,
                'data': data,
                'transaction_hash': tx_hash,
                'block_number': self.block_number,
                'timestamp': datetime.now().isoformat(),
                'verified': False,
                'network': self.network_name,
                'type': 'FRA_DOCUMENT'
            }
            
            # Add transaction
            self.transactions.append({
                'hash': tx_hash,
                'type': 'Document Registration',
                'holder': data.get('holder_name', data.get('name', 'Unknown')),
                'village': data.get('village_name', data.get('village', 'Unknown')),
                'district': data.get('district', 'Unknown'),
                'state': data.get('state', 'Unknown'),
                'timestamp': datetime.now().isoformat(),
                'status': 'Confirmed',
                'block_number': self.block_number
            })
            
            self.block_number += 1
            
            return {
                'success': True,
                'document_hash': doc_hash,
                'transaction_hash': tx_hash,
                'block_number': self.block_number - 1,
                'message': 'Document successfully registered on blockchain'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to register document on blockchain'
            }
    
    def verify_document(self, doc_hash, is_valid=True, notes='', verified_by='Admin'):
        """Verify a document on the blockchain"""
        try:
            if doc_hash not in self.documents:
                return {
                    'success': False,
                    'error': 'Document not found',
                    'message': 'Document hash not found in blockchain'
                }
            
            # Create verification transaction hash
            tx_hash = f"0x{hashlib.sha256(f'{doc_hash}_verify_{datetime.now().timestamp()}'.encode()).hexdigest()[:40]}"
            
            # Update document
            self.documents[doc_hash]['verified'] = is_valid
            self.documents[doc_hash]['verification_notes'] = notes
            self.documents[doc_hash]['verification_tx'] = tx_hash
            self.documents[doc_hash]['verified_by'] = verified_by
            self.documents[doc_hash]['verification_timestamp'] = datetime.now().isoformat()
            
            # Add verification transaction
            self.transactions.append({
                'hash': tx_hash,
                'type': 'Document Verification',
                'holder': self.documents[doc_hash]['data'].get('holder_name', self.documents[doc_hash]['data'].get('name', 'Unknown')),
                'village': self.documents[doc_hash]['data'].get('village_name', self.documents[doc_hash]['data'].get('village', 'Unknown')),
                'district': self.documents[doc_hash]['data'].get('district', 'Unknown'),
                'state': self.documents[doc_hash]['data'].get('state', 'Unknown'),
                'timestamp': datetime.now().isoformat(),
                'status': 'Confirmed',
                'result': 'Valid' if is_valid else 'Invalid',
                'verified_by': verified_by,
                'notes': notes,
                'block_number': self.block_number
            })
            
            self.block_number += 1
            
            return {
                'success': True,
                'verification_tx': tx_hash,
                'block_number': self.block_number - 1,
                'message': f'Document {"verified" if is_valid else "rejected"} on blockchain'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to verify document on blockchain'
            }
    
    def get_document(self, doc_hash):
        """Retrieve document information from blockchain"""
        if doc_hash in self.documents:
            return {
                'success': True,
                'document': self.documents[doc_hash]
            }
        else:
            return {
                'success': False,
                'error': 'Document not found'
            }
    
    def get_stats(self):
        """Get blockchain network statistics"""
        return {
            'total_documents': len(self.documents),
            'total_transactions': len(self.transactions),
            'verified_documents': sum(1 for doc in self.documents.values() if doc['verified']),
            'pending_documents': sum(1 for doc in self.documents.values() if not doc['verified']),
            'block_number': self.block_number,
            'network_name': self.network_name,
            'network_status': 'Active',
            'last_transaction': self.transactions[-1]['timestamp'] if self.transactions else None
        }
    
    def get_recent_transactions(self, limit=10):
        """Get recent blockchain transactions"""
        return {
            'success': True,
            'transactions': self.transactions[-limit:] if self.transactions else []
        }
    
    def search_documents(self, query):
        """Search documents by holder name, village, or district"""
        results = []
        query_lower = query.lower()
        
        for doc_hash, doc in self.documents.items():
            data = doc['data']
            if (query_lower in data.get('holder_name', '').lower() or
                query_lower in data.get('name', '').lower() or
                query_lower in data.get('village_name', '').lower() or
                query_lower in data.get('village', '').lower() or
                query_lower in data.get('district', '').lower()):
                results.append({
                    'hash': doc_hash,
                    'holder': data.get('holder_name', data.get('name', 'Unknown')),
                    'village': data.get('village_name', data.get('village', 'Unknown')),
                    'district': data.get('district', 'Unknown'),
                    'verified': doc['verified'],
                    'timestamp': doc['timestamp']
                })
        
        return {
            'success': True,
            'results': results,
            'count': len(results)
        }

# Initialize blockchain instance
blockchain = FRABlockchain()

def register_fra_document(data):
    """Register FRA document on blockchain"""
    return blockchain.register_document(data)

def verify_fra_document(doc_hash, is_valid=True, notes='', verified_by='Admin'):
    """Verify FRA document on blockchain"""
    return blockchain.verify_document(doc_hash, is_valid, notes, verified_by)

def get_blockchain_stats():
    """Get blockchain statistics"""
    return blockchain.get_stats()

def get_blockchain_transactions(limit=10):
    """Get recent blockchain transactions"""
    return blockchain.get_recent_transactions(limit)

def search_blockchain_documents(query):
    """Search blockchain documents"""
    return blockchain.search_documents(query)

def get_document_from_blockchain(doc_hash):
    """Get document from blockchain"""
    return blockchain.get_document(doc_hash)


