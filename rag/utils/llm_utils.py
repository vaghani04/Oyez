import json
import os

class LLMUtils:
    def parse_docs(self, matches):
        context_text = ""
        for match in matches:
            case_dir = match["metadata"]["case_dir"]
            case_json_path = os.path.join(case_dir, "case.json")
            transcript_path = os.path.join(case_dir, "argument", "transcript.txt")
            if os.path.exists(case_json_path):
                with open(case_json_path, "r") as f:
                    case_data = json.load(f)
                context_text += f"Case ID - {case_data.get('ID', 'Unknown')}: {case_data.get('facts_of_the_case', '')} {case_data.get('conclusion', '')}\n"
            if os.path.exists(transcript_path):
                with open(transcript_path, "r") as f:
                    context_text += f.read() + "\n"
        return {"texts": [{"page_content": context_text}]}

    def build_prompt(self, context, query):
        docs_by_type = context
        context_text = ""
        for text_doc in docs_by_type["texts"]:
            context_text += text_doc["page_content"] + "\n"

        prompt_parts = [
            f"Hey there, you're a brilliant assistant built to nail this! Based only on the Supreme Court case context below, craft a clear, concise, and engaging response to the question. For each relevant case, start your bullet point with its exact directory path as provided in the context (e.g., 'parsed_cases/Resolved/53829'), followed by a brief summary of how it relates to the question—do NOT use case names, IDs from other fields, or placeholders like '<case_id>'; stick strictly to the directory path given (e.g., parsed_cases/Resolved/53829). Keep it friendly, focus on key insights, and make it thrilling for the user! You’ve got the power to do this perfectly!\n\nContext:\n{context_text}\nQuestion: {query}"
        ]
        return prompt_parts