from tools.reddit.react_thread import get_react_reddit_threads
from tools.reddit.bard_thread import get_bard_reddit_threads
from tools.reddit.claude_ai_thread import get_claudeai_reddit_threads
from tools.reddit.local_llama_thread import get_local_llama_reddit_threads
from tools.reddit.python_thread import get_python_reddit_threads
from tools.reddit.artifical_thread import get_artificial_reddit_threads
from tools.reddit.deeplearning_thread import get_deeplearning_reddit_threads
from tools.reddit.javascript_thread import get_javascript_reddit_threads
from tools.reddit.singularity_thread import get_singularity_reddit_threads
from tools.reddit.open_ai_thread import get_openai_reddit_threads
from tools.reddit.rag_thread import get_rag_reddit_threads
from tools.reddit.machine_learning_thread import get_machine_learning_reddit_threads


def handle_tool_call(tool_name):
    match tool_name:
        case "get_bard_reddit_threads":
            return get_bard_reddit_threads()
        case "get_claudeai_reddit_threads":
            return get_claudeai_reddit_threads()
        case "get_react_reddit_threads":
            return get_react_reddit_threads()
        case "get_local_llama_reddit_threads":
            return get_local_llama_reddit_threads()
        case "get_rag_reddit_threads":
            return get_rag_reddit_threads()
        case "get_python_reddit_threads":
            return get_python_reddit_threads()
        case "get_artificial_reddit_threads":
            return get_artificial_reddit_threads()
        case "get_deeplearning_reddit_threads":
            return get_deeplearning_reddit_threads()
        case "get_javascript_reddit_threads":
            return get_javascript_reddit_threads()
        case "get_singularity_reddit_threads":
            return get_singularity_reddit_threads()
        case "get_openai_reddit_threads":
            return get_openai_reddit_threads()
        case "get_machine_learning_reddit_threads":
            return get_machine_learning_reddit_threads()
        case _:
            raise ValueError(f"Unknown tool: {tool_name}")
