"""
VESSA Security Incident Management SDK
Version: 1.0.0
"""

import json
import requests
from typing import Dict, List, Optional, Union, Any


class VessaApiError(Exception):
    """Exception raised for VESSA API errors."""
    
    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class VessaClient:
    """VESSA API client for security incident management."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.vessa.io"):
        """Initialize the VESSA client.
        
        Args:
            api_key: Your VESSA API key
            base_url: API base URL (default: https://api.vessa.io)
        """
        if not api_key:
            raise ValueError("API key is required")
            
        self.api_key = api_key
        self.base_url = base_url
    
    def request(self, method: str, path: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make an API request to the VESSA backend.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            data: Request data (for POST, PUT)
            params: Query parameters (for GET)
            
        Returns:
            API response data
            
        Raises:
            VessaApiError: If the API request fails
        """
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method.upper() != "GET" else None,
                params=params if method.upper() == "GET" else None
            )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_message = "API request failed"
            error_data = {}
            
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_message = error_data["detail"]
            except:
                pass
                
            raise VessaApiError(
                message=error_message,
                status_code=response.status_code,
                response=error_data
            )
        except requests.exceptions.RequestException as e:
            raise VessaApiError(f"Request failed: {str(e)}")


class IncidentsResource:
    """Resource for managing security incidents."""
    
    def __init__(self, client: VessaClient):
        """Initialize the incidents resource.
        
        Args:
            client: VESSA API client
        """
        self.client = client
    
    def create(self, **kwargs) -> Dict:
        """Create a new security incident.
        
        Args:
            title: Incident title
            description: Incident description
            severity: Incident severity (low, medium, high, critical)
            tags: List of tags
            assets: List of affected assets
            
        Returns:
            Created incident data
        """
        return self.client.request("POST", "/api/incidents", data=kwargs)
    
    def list(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """List all incidents.
        
        Args:
            limit: Maximum number of incidents to return
            offset: Number of incidents to skip
            
        Returns:
            List of incidents
        """
        params = f"?limit={limit}&offset={offset}"
        return self.client.request("GET", f"/api/incidents{params}")
    
    def get(self, incident_id: str) -> Dict:
        """Get an incident by ID.
        
        Args:
            incident_id: Incident ID
            
        Returns:
            Incident details
        """
        return self.client.request("GET", f"/api/incidents/{incident_id}")
    
    def update(self, incident_id: str, **kwargs) -> Dict:
        """Update an incident.
        
        Args:
            incident_id: Incident ID
            **kwargs: Fields to update
            
        Returns:
            Updated incident data
        """
        return self.client.request("PUT", f"/api/incidents/{incident_id}", data=kwargs)
    
    def add_tag(self, incident_id: str, tag: str) -> Dict:
        """Add a tag to an incident.
        
        Args:
            incident_id: Incident ID
            tag: Tag to add
            
        Returns:
            Updated incident data
        """
        return self.client.request("POST", f"/api/incidents/{incident_id}/tags/{tag}")
    
    def add_asset(self, incident_id: str, asset: str) -> Dict:
        """Add an affected asset to an incident.
        
        Args:
            incident_id: Incident ID
            asset: Asset to add
            
        Returns:
            Updated incident data
        """
        return self.client.request("POST", f"/api/incidents/{incident_id}/assets/{asset}")