/* eslint-disable */
import * as Router from 'expo-router';

export * from 'expo-router';

declare module 'expo-router' {
  export namespace ExpoRouter {
    export interface __routes<T extends string = string> extends Record<string, unknown> {
      StaticRoutes: `/` | `/(modals)` | `/(modals)/settings` | `/(modals)/tips` | `/(tabs)` | `/(tabs)/closet` | `/(tabs)/home` | `/(tabs)/profile` | `/_sitemap` | `/add-item` | `/auth/signin` | `/closet` | `/confirm-item` | `/home` | `/profile` | `/settings` | `/start` | `/tips` | `/webview/shop`;
      DynamicRoutes: `/item/${Router.SingleRoutePart<T>}`;
      DynamicRouteTemplate: `/item/[id]`;
    }
  }
}
