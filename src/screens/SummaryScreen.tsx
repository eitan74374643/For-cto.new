import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Button, Share } from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import { useStore } from '../store';
import { VoiceMessage } from '../types';

type ParamList = {
  Detail: { messageId: string };
};

export const SummaryScreen = () => {
  const route = useRoute<RouteProp<ParamList, 'Detail'>>();
  const { history } = useStore();
  const [message, setMessage] = useState<VoiceMessage | null>(null);

  useEffect(() => {
    const found = history.find((m) => m.id === route.params.messageId);
    if (found) setMessage(found);
  }, [route.params.messageId, history]);

  if (!message) return <View style={styles.container}><Text>Loading...</Text></View>;

  const handleShare = async () => {
    try {
      await Share.share({
        message: `Summary:\n${message.summary}\n\nTranscription:\n${message.transcription}`,
      });
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.section}>
        <Text style={styles.label}>Summary</Text>
        <Text style={styles.text}>{message.summary}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Transcription</Text>
        <Text style={styles.text}>{message.transcription}</Text>
      </View>

      <Button title="Share Text" onPress={handleShare} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  label: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333',
  },
  text: {
    fontSize: 16,
    lineHeight: 24,
    color: '#444',
  },
});
