import SwiftUI

struct MoreView: View {
    var body: some View {
        List {
            NavigationLink(destination: CanvasView()) {
                Label("Canvas", systemImage: "cpu")
            }
            NavigationLink(destination: ChatView()) {
                Label("Ask AI", systemImage: "bubble.left.and.bubble.right.fill")
            }
            NavigationLink(destination: AccountScreen()) {
                Label("Account", systemImage: "person")
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