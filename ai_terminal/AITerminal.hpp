#ifndef AI_TERMINAL_HPP
#define AI_TERMINAL_HPP

#include <string>
#include <vector>

// Structure to encapsulate the parsed output
struct CommandPayload {
    bool success = false;
    std::string command = "";
    std::string error_message = "";
};

class GroqClient {
public:
    explicit GroqClient(std::string api_key);
    std::string fetch_command(const std::string& prompt) const;

private:
    std::string api_key_;
    std::string build_json_payload(const std::string& prompt) const;
};

class ResponseParser {
public:
    static CommandPayload parse_json_response(const std::string& raw_response);
    static std::vector<std::string> tokenize_command(const std::string& command_str);
};

class CommandExecutor {
public:
    static bool execute(const std::vector<std::string>& tokens);
};

class TerminalApp {
public:
    void run();
};

#endif // AI_TERMINAL_HPP
