import SwiftUI

struct ProfileSettingsView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject var userSettings: UserSettings
    @AppStorage("userEmail") private var userEmail: String = ""
    
    var body: some View {
        NavigationStack {
            Form {
                Section(header: Text("Account")) {
                    Text("Email: \(userEmail)")
                    Button("Sign Out") {
                        // Handle sign out
                    }
                }
                
                Section(header: Text("Preferences")) {
                    Toggle("Use Metric System", isOn: $userSettings.useMetricSystem)
                    // Add other settings...
                }
                
                Section(header: Text("About")) {
                    NavigationLink("Privacy Policy") {
                        Text("Privacy Policy Content")
                    }
                    NavigationLink("Terms of Service") {
                        Text("Terms of Service Content")
                    }
                    Text("Version 1.0.0")
                }
            }
            .navigationTitle("Settings")
            .toolbar {
                Button("Done") {
                    isPresented = false
                }
            }
        }
    }
}

struct ProfileSettingsView_Previews: PreviewProvider {
    static var previews: some View {
        ProfileSettingsView(isPresented: .constant(true))
            .environmentObject(UserSettings())
    }
} 