

**AI-Powered Terminal | C++, Linux, Groq API, POSIX**
    AI TERMINAL
    An api calling based terminal. (don't know the command no worries , just prompt and it will execute the command)
    Based on REST API, internal syscalls

* Developed an AI-powered Linux terminal in **C++** that converts natural-language user prompts into executable Bash commands using the **Groq LLM API**.
* Implemented **HTTP API integration with `curl`**, JSON response parsing, command tokenization, and environment-based API-key management.
* Used **POSIX system calls (`fork`, `pipe`, `dup2`, `execvp`, `waitpid`)** for inter-process communication, process creation, output redirection, and isolated command execution.
* Designed a modular architecture separating **API client, response parser, command executor, and terminal application** components.
 
