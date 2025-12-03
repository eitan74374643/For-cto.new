import React, { useState } from 'react';
import { View, Text, StyleSheet, Button, ActivityIndicator, Alert } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { useStore } from '../store';
import { transcribeAudio, summarizeText } from '../services/ai';
import { VoiceMessage } from '../types';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

export const HomeScreen = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const addMessage = useStore((state) => state.addMessage);
  const navigation = useNavigation<NativeStackNavigationProp<any>>();

  const handlePickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'audio/*',
        copyToCacheDirectory: true,
      });

      if (result.canceled) return;

      const file = result.assets[0];
      processFile(file.uri);
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Failed to pick file');
    }
  };

  const processFile = async (uri: string) => {
    setIsProcessing(true);
    try {
      // 1. Transcribe
      const transcription = await transcribeAudio(uri);
      
      // 2. Summarize
      const summary = await summarizeText(transcription);

      // 3. Save
      const newMessage: VoiceMessage = {
        id: Date.now().toString(),
        filePath: uri,
        transcription,
        summary,
        createdAt: Date.now(),
        status: 'completed',
      };

      await addMessage(newMessage);
      setIsProcessing(false);
      navigation.navigate('History');
    } catch (error) {
      console.error(error);
      setIsProcessing(false);
      Alert.alert('Error', 'Failed to process audio');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>VoiceSnap</Text>
      <Text style={styles.subtitle}>
        Share a voice message to this app or pick a file below to summarize it.
      </Text>

      {isProcessing ? (
        <View style={styles.processing}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.processingText}>Processing audio...</Text>
        </View>
      ) : (
        <Button title="Pick Audio File" onPress={handlePickDocument} />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 40,
    color: '#666',
  },
  processing: {
    alignItems: 'center',
  },
  processingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
});
