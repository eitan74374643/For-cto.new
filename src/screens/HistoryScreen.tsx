import React, { useEffect } from 'react';
import { View, FlatList, StyleSheet, Text } from 'react-native';
import { useStore } from '../store';
import { MessageCard } from '../components/MessageCard';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

export const HistoryScreen = () => {
  const { history, loadHistory } = useStore();
  const navigation = useNavigation<NativeStackNavigationProp<any>>();

  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <View style={styles.container}>
      {history.length === 0 ? (
        <View style={styles.empty}>
            <Text style={styles.emptyText}>No history yet.</Text>
        </View>
      ) : (
        <FlatList
            data={history}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
            <MessageCard
                message={item}
                onPress={() => navigation.navigate('Summary', { messageId: item.id })}
            />
            )}
            contentContainerStyle={styles.list}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  list: {
    padding: 16,
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  }
});
