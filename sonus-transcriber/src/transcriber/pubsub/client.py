"""PubSub client implementation."""
import json
import time
import logging
from google.cloud import pubsub_v1
from ..config import PROJECT_ID, get_pubsub_config

logger = logging.getLogger('transcriber')

class PubSubClient:
    """Client for interacting with Google Cloud Pub/Sub."""
    
    def __init__(self):
        """Initialize the PubSub client."""
        self.project_id = PROJECT_ID
        pubsub_config = get_pubsub_config()
        self.topic_name = pubsub_config['topic']
        self.subscription_name = pubsub_config['subscription']
        
        # Initialize subscriber
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            self.project_id, self.subscription_name)
        
        # Initialize publisher (for potential future use)
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            self.project_id, self.topic_name)
        
        logger.debug(f"Initialized PubSub client for subscription: {self.subscription_name}")
    
    def pull_message(self, max_messages=1, wait_timeout=5):
        """Pull messages from the subscription.
        
        Args:
            max_messages: Maximum number of messages to pull
            wait_timeout: How long to wait in seconds if no messages are initially available
            
        Returns:
            List of received messages or empty list if none
        """
        try:
            # First try to get messages immediately
            response = self.subscriber.pull(
                request={
                    "subscription": self.subscription_path,
                    "max_messages": max_messages,
                    "return_immediately": True,
                }
            )
            
            if not response.received_messages and wait_timeout > 0:
                # If no messages, wait and try one more time
                logger.debug(f"No messages available, waiting {wait_timeout} seconds")
                time.sleep(wait_timeout)
                response = self.subscriber.pull(
                    request={
                        "subscription": self.subscription_path,
                        "max_messages": max_messages,
                        "return_immediately": True,
                    }
                )
            
            return response.received_messages
            
        except Exception as e:
            logger.error(f"Error pulling messages: {str(e)}")
            raise
    
    def acknowledge_message(self, ack_id):
        """Acknowledge a message.
        
        Args:
            ack_id: The acknowledgement ID of the message
        """
        try:
            self.subscriber.acknowledge(
                request={
                    "subscription": self.subscription_path,
                    "ack_ids": [ack_id],
                }
            )
            logger.debug(f"Message acknowledged (ACK ID: {ack_id})")
        except Exception as e:
            logger.error(f"Error acknowledging message: {str(e)}")
            raise
    
    def publish_message(self, message_data):
        """Publish a message to the topic.
        
        Args:
            message_data: Dictionary with message data
            
        Returns:
            The published message ID
        """
        try:
            message_json = json.dumps(message_data).encode("utf-8")
            future = self.publisher.publish(self.topic_path, message_json)
            message_id = future.result()
            logger.debug(f"Published message to {self.topic_path} with ID: {message_id}")
            return message_id
        except Exception as e:
            logger.error(f"Error publishing message: {str(e)}")
            raise
    
    def close(self):
        """Close the subscriber client."""
        try:
            self.subscriber.close()
            logger.debug("PubSub subscriber client closed")
        except Exception as e:
            logger.debug(f"Error closing subscriber: {str(e)}")
