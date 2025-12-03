import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { VoiceMessage } from '../types';

interface Props {
  message: VoiceMessage;
  onPress: () => void;
}

export const MessageCard: React.FC<Props> = ({ message, onPress }) => {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <Text style={styles.date}>{new Date(message.createdAt).toLocaleString()}</Text>
      <Text style={styles.summary} numberOfLines={2}>{message.summary}</Text>
      <Text style={styles.status}>{message.status}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  date: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  summary: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  status: {
    fontSize: 12,
    color: '#999',
    marginTop: 8,
    textAlign: 'right',
  },
});
