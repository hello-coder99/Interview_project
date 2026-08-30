#include "AITerminal.hpp"
#include <iostream>
#include <unistd.h>
#include <sys/wait.h>
#include <cstring>
#include <sstream>

// ==========================================
// 1. API CLIENT IMPLEMENTATION
// ==========================================
GroqClient::GroqClient(std::string api_key) : api_key_(std::move(api_key)) {}

std::string GroqClient::build_json_payload(const std::string& prompt) const {
    // Escaping quotes securely requires a JSON library, but for a lightweight inline implementation,
    // we use clean raw string literals.
    return R"({
        "messages": [{
            "role": "user",
            "content": ")" + prompt + R"(, Just write the bash command in format command: <command>"
        }],
        "model": "openai/gpt-oss-120b"
    })";
}

std::string GroqClient::fetch_command(const std::string& prompt) const {
    int pipe_fds[2];
    if (pipe(pipe_fds) == -1) {
        perror("[Error] Failed to initialize pipeline infrastructure");
        return "";
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("[Error] Fork system invocation failed");
        close(pipe_fds[0]);
        close(pipe_fds[1]);
        return "";
    }

    if (pid == 0) { // Child Process Context
        close(pipe_fds[0]);
        if (dup2(pipe_fds[1], STDOUT_FILENO) == -1) {
            perror("[Child Error] Standard output redirection failed");
            exit(EXIT_FAILURE);
        }
        close(pipe_fds[1]);

        std::string json_payload = build_json_payload(prompt);
        std::string auth_header = "Authorization: Bearer " + api_key_;

        // Elements explicitly pointed to prevent volatile optimization issues 
        std::vector<const char*> args = {
            "curl", "-s", "-X", "POST",
            "https://api.groq.com/openai/v1/chat/completions",
            "-H", "Content-Type: application/json",
            "-H", auth_header.c_str(),
            "-d", json_payload.c_str(),
            nullptr
        };

        execvp(args[0], const_cast<char* const*>(args.data()));
        perror("[Child Error] Execution deployment of curl failed");
        exit(EXIT_FAILURE); 
    } 
    
    // Parent Process Context
    close(pipe_fds[1]);
    std::string raw_response;
    char chunk_buffer[4096];
    ssize_t read_bytes;

    while ((read_bytes = read(pipe_fds[0], chunk_buffer, sizeof(chunk_buffer) - 1)) > 0) {
        chunk_buffer[read_bytes] = '\0';
        raw_response.append(chunk_buffer);
    }
    close(pipe_fds[0]);
    waitpid(pid, nullptr, 0);

    return raw_response;
}

// ==========================================
// 2. PARSER IMPLEMENTATION
// ==========================================
CommandPayload ResponseParser::parse_json_response(const std::string& raw_response) {
    CommandPayload payload;
    const std::string content_marker = "\"content\":\"";
    
    size_t target_start = raw_response.find(content_marker);
    if (target_start == std::string::npos) {
        payload.error_message = "Malformed payload signature received from API.";
        return payload;
    }
    target_start += content_marker.length();

    size_t target_end = raw_response.find("\"", target_start);
    if (target_end == std::string::npos) {
        payload.error_message = "Unterminated token stream isolated in structural string extraction.";
        return payload;
    }

    std::string structural_content = raw_response.substr(target_start, target_end - target_start);
    size_t protocol_separator = structural_content.find(':');
    
    if (protocol_separator != std::string::npos) {
        payload.command = structural_content.substr(protocol_separator + 1);
        // Stripping structural leading space buffers if present
        if (!payload.command.empty() && payload.command[0] == ' ') {
            payload.command.erase(0, 1);
        }
        payload.success = true;
    } else {
        payload.error_message = "Target protocol header prefix ('command:') missing.";
    }

    return payload;
}

std::vector<std::string> ResponseParser::tokenize_command(const std::string& command_str) {
    std::vector<std::string> tokens;
    std::string current_token;
    bool inside_quotes = false;

    for (size_t i = 0; i < command_str.length(); ++i) {
        char current_char = command_str[i];

        if (current_char == '"') {
            inside_quotes = !inside_quotes; // Toggle state
            continue; 
        }

        if (current_char == ' ' && !inside_quotes) {
            if (!current_token.empty()) {
                tokens.push_back(current_token);
                current_token.clear();
            }
        } else {
            current_token.push_back(current_char);
        }
    }
    if (!current_token.empty()) {
        tokens.push_back(current_token);
    }
    return tokens;
}

// ==========================================
// 3. EXECUTOR IMPLEMENTATION
// ==========================================
bool CommandExecutor::execute(const std::vector<std::string>& tokens) {
    if (tokens.empty()) return false;

    pid_t worker_pid = fork();
    if (worker_pid < 0) {
        perror("[Error] Subprocess fork deployment blocked");
        return false;
    }

    if (worker_pid == 0) { // Child context
        std::vector<char*> argument_vector;
        argument_vector.reserve(tokens.size() + 1);

        for (const auto& token : tokens) {
            argument_vector.push_back(const_cast<char*>(token.c_str()));
        }
        argument_vector.push_back(nullptr);

        execvp(argument_vector[0], argument_vector.data());
        perror("[Runtime Error] Selected binary failed execution state");
        exit(EXIT_FAILURE); // Prevent catastrophic child fall-through into terminal input loop
    }

    int execution_status;
    waitpid(worker_pid, &execution_status, 0);
    return WIFEXITED(execution_status) && WEXITSTATUS(execution_status) == 0;
}

// ==========================================
// 4. MAIN APP FLOW INTERFACE
// ==========================================
void TerminalApp::run() {
    // Securely source API key from system environment variables
    const char* env_key = std::getenv("GROQ_API_KEY");
    if (!env_key) {
        std::cerr << "[Fatal] Environment variable 'GROQ_API_KEY' is missing.\nExiting context.\n";
        return;
    }

    GroqClient client(env_key);
    std::string user_prompt;

    while (true) {
        std::cout << "ai-terminal>>> ";
        if (!std::getline(std::cin, user_prompt)) break;

        if (user_prompt == "exit" || user_prompt == "quit") {
            break;
        }
        if (user_prompt.empty()) continue;

        std::string raw_json = client.fetch_command(user_prompt);
        if (raw_json.empty()) continue;

        CommandPayload outcome = ResponseParser::parse_json_response(raw_json);
        if (!outcome.success) {
            std::cerr << "[Parser Alert] " << outcome.error_message << "\n";
            continue;
        }

        std::cout << "Executing: " << outcome.command << "\n";
        std::vector<std::string> formatted_tokens = ResponseParser::tokenize_command(outcome.command);
        
        CommandExecutor::execute(formatted_tokens);
    }
}
