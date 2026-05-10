"""Credential service for the agents package."""

from google.adk.auth.credential_service.in_memory_credential_service import (
    InMemoryCredentialService,
)

credential_service = InMemoryCredentialService()
