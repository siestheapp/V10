import SwiftUI

struct ClosetView: View {
    @State private var selectedTab = 0
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Scan Tab
            ScanTab()
                .tabItem {
                    Label("Scan", systemImage: "camera")
                }
                .tag(0)
            
            // Finds Tab
            ScanHistoryView()
                .tabItem {
                    Label("Finds", systemImage: "list.bullet")
                }
                .tag(1)
            
            // Closet Tab
            ClosetListView()
                .tabItem {
                    Label("Closet", systemImage: "tshirt")
                }
                .tag(2)
            
            // Fit Tab
            UserMeasurementProfileView()
                .tabItem {
                    Label("Fit", systemImage: "ruler")
                }
                .tag(3)
            
            // Account Tab (replacing Match)
            AccountScreen()
                .tabItem {
                    Label("Match", systemImage: "link")
                }
                .tag(4)
        }
        .overlay(
            Group {
                if isLoading {
                    ProgressView()
                }
                if showError {
                    Text(errorMessage)
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.red)
                        .cornerRadius(8)
                }
            }
        )
    }
}

#Preview {
    ClosetView()
} 