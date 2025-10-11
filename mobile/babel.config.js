module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      // Do NOT include 'expo-router/babel' on SDK 50/51
      'react-native-reanimated/plugin', // must be last
    ],
  };
};
