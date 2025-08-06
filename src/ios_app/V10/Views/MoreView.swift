import SwiftUI

struct MoreView: View {
    var body: some View {
        List {
            NavigationLink(destination: ScanHistoryView()) {
                Label("Scan History", systemImage: "list.bullet")
            }
            NavigationLink(destination: ChatView()) {
                Label("Ask AI", systemImage: "bubble.left.and.bubble.right.fill")
            }
            NavigationLink(destination: AccountScreen()) {
                Label("Account", systemImage: "person")
            }
            NavigationLink(destination: BodyScreen()) {
                Label("Body", systemImage: "figure.stand")
            }
        }
        .navigationTitle("More")
    }
}

struct MoreView_Previews: PreviewProvider {
    static var previews: some View {
        MoreView()
    }
} 