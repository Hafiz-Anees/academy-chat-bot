"""Message processing: text and voice, both routed through the same RAG flow."""
from core.rag_chain import get_response
from core.whatsapp import send_whatsapp_message, download_media
from core.speech import transcribe_audio , synthesize_speech
from core.whatsapp import send_whatsapp_audio
from scripts.state import sessions, get_user_lock


"""Handles a text message: RAG response + reply."""

async def process_message(from_number: str, text: str):
    
    lock = get_user_lock(from_number)
    async with lock:
        history = sessions.setdefault(from_number, [])
        reply = get_response(text, chat_history=history)
        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": reply})
        send_whatsapp_message(from_number, reply)
        print(f"Sent WhatsApp message to {from_number}: {reply}")



"""Handles a voice note: download -> transcribe -> RAG -> reply as voice."""

async def process_voice_message(from_number: str, media_id: str):
    
    lock = get_user_lock(from_number)
    async with lock:
        try:
            audio_bytes = download_media(media_id)
            transcript = transcribe_audio(audio_bytes, language="en")
            print(f"Transcript from {from_number}: {transcript}")

            history = sessions.setdefault(from_number, [])
            reply = get_response(transcript, chat_history=history)
            history.append({"role": "user", "content": transcript})
            history.append({"role": "assistant", "content": reply})
            # fix the markdown formatting for audio reply, since WhatsApp doesn't support markdown in voice messages
            # reply = reply.replace("**", "").replace("*", "")  # Remove markdown formatting or can use llm to convert it into plain text
            reply_audio = synthesize_speech(reply)
            send_whatsapp_audio(from_number, reply_audio)
            print(f"Sent voice reply to {from_number}: {reply}")

        except Exception as e:
            print(f"ERROR processing voice message {media_id}: {type(e).__name__}: {e}")
            send_whatsapp_message(
                from_number,
                "Sorry, I couldn't understand that voice message. Could you try again or type your question?"
            )