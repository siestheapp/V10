import SwiftUI
import Foundation

// Networking function to register a user
func registerUser(email: String, password: String, name: String) {
    // Change the URL to match your FastAPI server
    guard let url = URL(string: "http://127.0.0.1:8000/register") else { return }
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    let userData: [String: Any] = [
        "email": email,
        "password": password,
        "name": name
    ]

    request.httpBody = try? JSONSerialization.data(withJSONObject: userData)

    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            print("Registration Error: \(error.localizedDescription)")
            return
        }

        if let httpResponse = response as? HTTPURLResponse {
            print("Status code: \(httpResponse.statusCode)")
        }

        if let data = data {
            print("Registration Response: \(String(data: data, encoding: .utf8) ?? "")")
        }
    }.resume()
}

struct EmailSignUpView: View {
    @State private var email = ""
    @State private var name = ""
    @State private var password = ""
    @State private var showUserDetailsView = false
    @State private var currentStep = 1
    
    var body: some View {
        if showUserDetailsView {
            UserDetailsView(goBack: {
                withAnimation {
                    showUserDetailsView = false
                }
            })
        } else {
            VStack(spacing: 20) {
                // Progress indicator
                HStack(spacing: 4) {
                    ForEach(1...3, id: \.self) { step in
                        Rectangle()
                            .frame(height: 4)
                            .foregroundColor(step <= currentStep ? .blue : .gray.opacity(0.3))
                    }
                }
                .padding(.horizontal, 40)
                
                // Dynamic title based on step
                Text(stepTitle)
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                // Current step content
                VStack(spacing: 15) {
                    switch currentStep {
                    case 1:
                        TextField("Email", text: $email)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .keyboardType(.emailAddress)
                            .autocapitalization(.none)
                            .textContentType(.emailAddress)
                    case 2:
                        TextField("Name", text: $name)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.words)
                            .textContentType(.name)
                    case 3:
                        SecureField("Password", text: $password)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .textContentType(.newPassword)
                    default:
                        EmptyView()
                    }
                }
                .padding(.horizontal, 40)
                
                // Continue button
                Button(action: handleContinue) {
                    Text(currentStep == 3 ? "Create Account" : "Continue")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isCurrentStepValid ? Color.blue : Color.gray)
                        .cornerRadius(10)
                }
                .padding(.horizontal, 40)
                .disabled(!isCurrentStepValid)
                
                // Back button for steps 2 and 3
                if currentStep > 1 {
                    Button(action: {
                        withAnimation {
                            currentStep -= 1
                        }
                    }) {
                        Text("Back")
                            .foregroundColor(.blue)
                    }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color(.systemBackground))
        }
    }
    
    private var stepTitle: String {
        switch currentStep {
        case 1: return "What's your email?"
        case 2: return "What's your name?"
        case 3: return "Create a password"
        default: return ""
        }
    }
    
    private var isCurrentStepValid: Bool {
        switch currentStep {
        case 1: return isValidEmail(email)
        case 2: return !name.isEmpty
        case 3: return isValidPassword(password)
        default: return false
        }
    }
    
    private func handleContinue() {
        if currentStep < 3 {
            withAnimation {
                currentStep += 1
            }
        } else {
            registerUser(email: email, password: password, name: name)
            showUserDetailsView = true
        }
    }
    
    private func isValidEmail(_ email: String) -> Bool {
        let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPred = NSPredicate(format:"SELF MATCHES %@", emailRegEx)
        return emailPred.evaluate(with: email)
    }
    
    private func isValidPassword(_ password: String) -> Bool {
        return password.count >= 4 // Changed from 8 to 4
    }
}

struct EmailSignUpView_Previews: PreviewProvider {
    static var previews: some View {
        EmailSignUpView()
    }
}
