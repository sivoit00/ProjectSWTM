from sqlalchemy.orm import Session
import models
import os
import openai
from fastapi import HTTPException

class OpenAIService:
    @staticmethod
    def openai_chat(message: str, db: Session):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured on server")

        try:
            openai.api_key = api_key
            model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            resp = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "user", "content": message}],
                max_tokens=600,
                temperature=0.7,
            )
            answer = resp.choices[0].message.content.strip()

            ki = models.KIAktion(nachricht=message, antwort=answer, auftrag_id=None)
            db.add(ki)
            db.commit()
            db.refresh(ki)

            return {"response": answer}
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print("OpenAI call failed:", tb)
            
            detail = str(e)
            try:
                if hasattr(e, 'user_message'):
                    detail = e.user_message
                elif hasattr(e, 'error') and isinstance(e.error, dict) and 'message' in e.error:
                    detail = e.error['message']
            except Exception:
                pass
            raise HTTPException(status_code=500, detail=detail)
