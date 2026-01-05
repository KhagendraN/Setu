from fastapi import APIRouter, HTTPException, Depends
from api.core.deps import get_current_user
from api.schemas import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse
)
from api.routes.supabase_auth import get_supabase_admin
from typing import List

router = APIRouter()

# ============================================================
# Conversation Endpoints
# ============================================================

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    user: dict = Depends(get_current_user)
):
    """Create a new conversation for the authenticated user."""
    try:
        supabase = get_supabase_admin()

        result = supabase.table("chat_conversations").insert({
            "user_id": user["id"],
            "title": request.title
        }).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create conversation")

        conversation_data = result.data[0]
        conversation_data["message_count"] = 0
        return conversation_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    limit: int = 50,
    offset: int = 0,
    user: dict = Depends(get_current_user)
):
    """Get all conversations for the authenticated user."""
    try:
        supabase = get_supabase_admin()

        # Get conversations
        conv_result = supabase.table("chat_conversations")\
            .select("*")\
            .eq("user_id", user["id"])\
            .order("updated_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        conversations = []
        for conv in conv_result.data:
            # Get message count for each conversation
            msg_count = supabase.table("chat_messages")\
                .select("id", count="exact")\
                .eq("conversation_id", conv["id"])\
                .execute()

            conv["message_count"] = msg_count.count if msg_count.count else 0
            conversations.append(conv)

        return conversations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user)
):
    """Get a specific conversation with all its messages."""
    try:
        supabase = get_supabase_admin()

        # Get conversation
        conv_result = supabase.table("chat_conversations")\
            .select("*")\
            .eq("id", conversation_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conversation = conv_result.data[0]

        # Get messages
        messages_result = supabase.table("chat_messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("timestamp")\
            .execute()

        return {
            **conversation,
            "messages": messages_result.data,
            "message_count": len(messages_result.data)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdate,
    user: dict = Depends(get_current_user)
):
    """Update conversation details (e.g., title)."""
    try:
        supabase = get_supabase_admin()

        # Verify ownership
        conv_check = supabase.table("chat_conversations")\
            .select("id")\
            .eq("id", conversation_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not conv_check.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Build update dict
        update_dict = {}
        if request.title is not None:
            update_dict["title"] = request.title

        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update conversation
        result = supabase.table("chat_conversations")\
            .update(update_dict)\
            .eq("id", conversation_id)\
            .execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to update conversation")

        conversation_data = result.data[0]
        conversation_data["message_count"] = None
        return conversation_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a conversation and all its messages."""
    try:
        supabase = get_supabase_admin()

        # Delete conversation (messages cascade deleted)
        result = supabase.table("chat_conversations")\
            .delete()\
            .eq("id", conversation_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"success": True, "message": "Conversation deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Message Endpoints
# ============================================================

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    request: MessageCreate,
    user: dict = Depends(get_current_user)
):
    """Add a message to a conversation."""
    try:
        supabase = get_supabase_admin()

        # Verify conversation ownership
        conv_check = supabase.table("chat_conversations")\
            .select("id")\
            .eq("id", conversation_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not conv_check.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Validate role
        if request.role not in ["user", "assistant"]:
            raise HTTPException(status_code=400, detail="Role must be 'user' or 'assistant'")

        # Insert message
        message_data = {
            "conversation_id": conversation_id,
            "role": request.role,
            "content": request.content
        }

        if request.metadata:
            message_data["metadata"] = request.metadata

        result = supabase.table("chat_messages")\
            .insert(message_data)\
            .execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create message")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = 100,
    offset: int = 0,
    user: dict = Depends(get_current_user)
):
    """Get all messages in a conversation."""
    try:
        supabase = get_supabase_admin()

        # Verify conversation ownership
        conv_check = supabase.table("chat_conversations")\
            .select("id")\
            .eq("id", conversation_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not conv_check.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get messages
        result = supabase.table("chat_messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("timestamp")\
            .range(offset, offset + limit - 1)\
            .execute()

        return result.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a specific message."""
    try:
        supabase = get_supabase_admin()

        # Get message to verify ownership
        message_result = supabase.table("chat_messages")\
            .select("conversation_id")\
            .eq("id", message_id)\
            .execute()

        if not message_result.data:
            raise HTTPException(status_code=404, detail="Message not found")

        conversation_id = message_result.data[0]["conversation_id"]

        # Verify conversation ownership
        conv_check = supabase.table("chat_conversations")\
            .select("id")\
            .eq("id", conversation_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not conv_check.data:
            raise HTTPException(status_code=403, detail="Permission denied")

        # Delete message
        supabase.table("chat_messages")\
            .delete()\
            .eq("id", message_id)\
            .execute()

        return {"success": True, "message": "Message deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
