import SwiftUI

struct EmailSignUpView: View {
    @State private var email = ""
    @State private var showUserDetailsView = false
    @State private var showPasswordView = false
    
    var body: some View {
        if showUserDetailsView {
            UserDetailsView(goBack: {
                withAnimation {
                    showUserDetailsView = false
                    showPasswordView = true
                }
            })
        } else if showPasswordView {
            CreatePasswordView(showUserDetailsView: $showUserDetailsView, goBack: {
                withAnimation {
                    showPasswordView = false
                }
            })
        } else {
            VStack(spacing: 30) {
                Text("Enter your email")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                TextField("Email", text: $email)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)
                    .padding(.horizontal, 40)
                
                Button(action: {
                    withAnimation {
                        showPasswordView = true
                    }
                }) {
                    Text("Submit")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .padding(.horizontal, 40)
                .disabled(email.isEmpty)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color(.systemBackground))
        }
    }
} 
