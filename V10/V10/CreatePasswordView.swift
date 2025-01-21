import SwiftUI

struct CreatePasswordView: View {
    @Binding var showUserDetailsView: Bool
    @State private var password = ""
    @State private var confirmPassword = ""
    var goBack: () -> Void
    
    var body: some View {
        ZStack(alignment: .topLeading) {
            Button(action: goBack) {
                Image(systemName: "chevron.left")
                    .font(.title2)
                    .foregroundColor(.blue)
                    .padding()
            }
            
            VStack(spacing: 30) {
                Text("Create a password")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                VStack(spacing: 20) {
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .padding(.horizontal, 40)
                    
                    SecureField("Confirm password", text: $confirmPassword)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .padding(.horizontal, 40)
                }
                
                Button(action: {
                    withAnimation {
                        showUserDetailsView = true
                    }
                }) {
                    Text("Continue")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .padding(.horizontal, 40)
                .disabled(password.isEmpty || password != confirmPassword)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color(.systemBackground))
        }
    }
} 