import { useMutation } from '@tanstack/react-query';
import { useCallback, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Keyboard,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import ProductSummary from '../../components/Scan/ProductSummary';
import supabase from '../../lib/supabase';
import { fetchProductByUrl, normalizeUrl, ProductResult } from '../../lib/product';

export default function ScanScreen() {
  const [inputUrl, setInputUrl] = useState('');

  const lookup = useMutation<ProductResult[], Error, string>({
    mutationKey: ['product-by-url'],
    mutationFn: (value) => fetchProductByUrl(supabase, value),
  });

  const handleSubmit = useCallback(() => {
    const normalized = normalizeUrl(inputUrl);
    if (!normalized) return;
    setInputUrl(normalized);
    Keyboard.dismiss();
    lookup.mutate(normalized);
  }, [inputUrl, lookup]);

  const buttonDisabled = !inputUrl.trim() || lookup.isPending;
  const product = useMemo(() => (lookup.data && lookup.data.length ? lookup.data[0] : undefined), [lookup.data]);
  const showNotFound = lookup.isSuccess && (!lookup.data || lookup.data.length === 0);

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Paste a product link to start a try-on.</Text>
      <TextInput
        value={inputUrl}
        onChangeText={setInputUrl}
        placeholder="https://brand.com/product"
        autoCapitalize="none"
        autoCorrect={false}
        clearButtonMode="while-editing"
        keyboardType="url"
        returnKeyType="go"
        onSubmitEditing={handleSubmit}
        style={styles.input}
      />
      <TouchableOpacity style={[styles.button, buttonDisabled && styles.buttonDisabled]} disabled={buttonDisabled} onPress={handleSubmit}>
        {lookup.isPending ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Start Try-On</Text>}
      </TouchableOpacity>

      {lookup.isError ? (
        <Text style={styles.feedback}>Something went wrong: {lookup.error.message}</Text>
      ) : null}

      {showNotFound ? <Text style={styles.feedback}>We couldn’t find that product. Double-check the link and try again.</Text> : null}

      {product ? <ProductSummary product={product} /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  heading: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 12,
    color: '#222',
  },
  input: {
    borderWidth: 1,
    borderColor: '#d0d0d0',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    marginBottom: 12,
    fontSize: 16,
  },
  button: {
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#111',
  },
  buttonDisabled: {
    backgroundColor: '#999',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  feedback: {
    marginTop: 16,
    color: '#555',
    textAlign: 'center',
  },
});
