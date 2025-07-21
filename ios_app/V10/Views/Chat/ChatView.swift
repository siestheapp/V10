import SwiftUI

struct Message: Identifiable {
    let id = UUID()
    let content: String
    let isUser: Bool
    let timestamp = Date()
}

struct ChatView: View {
    @State private var messages: [Message] = []
    @State private var newMessage = ""
    @State private var isLoading = false
    @EnvironmentObject var userSettings: UserSettings
    
    // Updated to use IPv4 localhost address explicitly
    private let baseURL = "http://127.0.0.1:8006"
    
    var body: some View {
        NavigationView {
            VStack {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(messages) { message in
                            MessageBubble(message: message)
                        }
                        
                        if isLoading {
                            ProgressView()
                                .padding()
                        }
                    }
                    .padding()
                }
                
                VStack(spacing: 0) {
                    Divider()
                    HStack {
                        TextField("Ask about measurements...", text: $newMessage)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .disabled(isLoading)
                        
                        Button(action: sendMessage) {
                            Image(systemName: "arrow.up.circle.fill")
                                .font(.system(size: 24))
                                .foregroundColor(newMessage.isEmpty ? .gray : .blue)
                        }
                        .disabled(newMessage.isEmpty || isLoading)
                    }
                    .padding()
                }
            }
            .navigationTitle("Measurement Assistant")
            .onAppear {
                // Add welcome message
                if messages.isEmpty {
                    messages.append(Message(
                        content: "Hi! I'm your measurement assistant. I can help you find the right measurements for any garment. What would you like to know?",
                        isUser: false
                    ))
                }
            }
        }
    }
    
    private func sendMessage() {
        let userMessage = newMessage.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !userMessage.isEmpty else { return }
        
        // Add user message
        messages.append(Message(content: userMessage, isUser: true))
        newMessage = ""
        isLoading = true
        
        // Call AI endpoint with improved networking
        Task {
            do {
                guard let url = URL(string: "\(baseURL)/chat/measurements") else {
                    throw URLError(.badURL)
                }
                
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                request.timeoutInterval = 30 // Increased timeout
                
                // Use default user ID if not set
                let userId = userSettings.userId == 0 ? 2 : userSettings.userId
                
                let body = [
                    "message": userMessage,
                    "user_id": userId
                ] as [String: Any]
                
                request.httpBody = try JSONSerialization.data(withJSONObject: body)
                
                let config = URLSessionConfiguration.default
                config.waitsForConnectivity = true // Wait for connection if offline
                config.timeoutIntervalForRequest = 30
                config.timeoutIntervalForResource = 300
                
                let session = URLSession(configuration: config)
                
                let (data, response) = try await session.data(for: request)
                
                guard let httpResponse = response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 else {
                    throw URLError(.badServerResponse)
                }
                
                let chatResponse = try JSONDecoder().decode(ChatResponse.self, from: data)
                
                DispatchQueue.main.async {
                    messages.append(Message(content: chatResponse.response, isUser: false))
                    isLoading = false
                }
            } catch {
                print("Network Error: \(error)")
                DispatchQueue.main.async {
                    messages.append(Message(
                        content: "Sorry, I encountered a connection error. Please check your network connection and try again.",
                        isUser: false
                    ))
                    isLoading = false
                }
            }
        }
    }
}

struct MessageBubble: View {
    let message: Message
    
    var body: some View {
        HStack {
            if message.isUser { Spacer() }
            
            Text(message.content)
                .padding()
                .background(message.isUser ? Color.blue : Color(.systemGray6))
                .foregroundColor(message.isUser ? .white : .primary)
                .cornerRadius(16)
            
            if !message.isUser { Spacer() }
        }
    }
}

struct ChatResponse: Codable {
    let response: String
} 