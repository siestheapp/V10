import Constants from 'expo-constants';

export const IS_DEMO: boolean = !!(Constants.expoConfig as any)?.extra?.DEMO;


