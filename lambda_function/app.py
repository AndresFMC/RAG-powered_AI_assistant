"""
AWS Lambda Handler for RAG-Powered AI Assistant
Thin wrapper around rag_core RAG pipeline.
"""

import json
import os
from rag_core.core.rag_pipeline import RAGPipeline

# Initialize pipeline once (outside handler for Lambda warm starts)
pipeline = None

def get_pipeline():
    """Get or create RAG pipeline instance."""
    global pipeline
    if pipeline is None:
        pipeline = RAGPipeline()
    return pipeline


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Expected event body format:
    {
        "country": "spain",
        "question": "What is the probation period?"
    }
    
    Or for stats endpoint:
    {
        "action": "stats"
    }
    
    Or for countries list:
    {
        "action": "list_countries"
    }
    """
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Get pipeline instance
        rag = get_pipeline()
        
        # Handle different actions
        action = body.get('action', 'query')
        
        if action == 'stats':
            # Get index statistics
            result = rag.get_index_stats()
            
        elif action == 'list_countries':
            # List available countries
            result = {
                'countries': rag.list_countries()
            }
            
        elif action == 'query':
            # Main RAG query
            country = body.get('country')
            question = body.get('question')
            
            if not country or not question:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
                    },
                    'body': json.dumps({
                        'error': 'Missing required fields: country and question'
                    })
                }
            
            top_k = body.get('top_k', 5)
            
            result = rag.query(
                country=country,
                question=question,
                top_k=top_k
            )
        
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'Unknown action: {action}'
                })
            }
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }