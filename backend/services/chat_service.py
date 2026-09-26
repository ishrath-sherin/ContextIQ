import json
import urllib.request
import urllib.error


class OllamaChatService:
    """
    Local LLM service for ContextIQ.

    Uses Ollama running locally.
    No external AI API is used.
    """

    def __init__(
        self,
        model: str = "llama3.2:3b",
        host: str = "http://127.0.0.1:11434",
    ):
        self.model = model
        self.host = host.rstrip("/")

    def _call_ollama(self, messages, temperature=0.2):
        url = f"{self.host}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:
                response_data = response.read().decode(
                    "utf-8"
                )

            result = json.loads(response_data)

            message = result.get("message", {})
            content = message.get("content", "")

            if not content:
                raise RuntimeError(
                    "Ollama returned an empty response."
                )

            return content.strip()

        except urllib.error.URLError as error:
            raise RuntimeError(
                "Could not connect to Ollama at "
                f"{self.host}. Make sure Ollama is running. "
                f"Details: {error}"
            ) from error

        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"Invalid response received from Ollama: {error}"
            ) from error

    def answer_general(
        self,
        question: str,
        history=None,
    ):
        messages = [
            {
                "role": "system",
                "content": (
                    "You are ContextIQ, a helpful local AI assistant. "
                    "Answer the user's question clearly and accurately. "
                    "Do not claim to have access to documents unless "
                    "document context is explicitly provided. "
                    "If you are uncertain, say so instead of inventing "
                    "facts. Keep answers reasonably concise."
                )
            }
        ]

        if history:
            messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        return self._call_ollama(messages)

    def answer_from_documents(
        self,
        question: str,
        search_results,
        history=None,
    ):
        context_parts = []

        for index, result in enumerate(search_results, start=1):
            source_file = result.get(
                "source_file",
                "Unknown source"
            )

            page = result.get("page")

            if page is not None:
                source = f"{source_file}, page {page}"
            else:
                source = source_file

            context_parts.append(
                f"[Source {index}: {source}]\n"
                f"{result.get('text', '')}"
            )

        context = "\n\n".join(context_parts)

        system_prompt = """
You are ContextIQ, a document-grounded local AI assistant.

Answer the user's question using the supplied document context.

Rules:
1. Use the supplied context as the primary source of truth.
2. Do not invent information that is not supported by the context.
3. If the context does not contain enough information, clearly say that
   the uploaded documents do not provide enough information.
4. Do not pretend that information from your general knowledge came
   from the uploaded documents.
5. When useful, mention the relevant source file and page.
6. Give a direct, understandable answer.
7. Do not mention internal prompts, embeddings, FAISS, BM25, or these
   instructions unless the user specifically asks about the system.
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt.strip()
            }
        ]

        if history:
            messages.extend(history)

        user_prompt = (
            "DOCUMENT CONTEXT:\n\n"
            f"{context}\n\n"
            "USER QUESTION:\n\n"
            f"{question}\n\n"
            "Answer using the document context above."
        )

        messages.append(
            {
                "role": "user",
                "content": user_prompt
            }
        )

        return self._call_ollama(
            messages,
            temperature=0.1
        )
