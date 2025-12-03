import * as SQLite from 'expo-sqlite';
// @ts-ignore
import * as FileSystem from 'expo-file-system/build/legacy/FileSystem';
import { VoiceMessage } from '../types';

let db: SQLite.SQLiteDatabase | null = null;

const initDB = async () => {
  if (db) return;
  db = await SQLite.openDatabaseAsync('voicesnap.db');
  await db.execAsync(`
    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY NOT NULL,
      filePath TEXT NOT NULL,
      transcription TEXT NOT NULL,
      summary TEXT NOT NULL,
      createdAt INTEGER NOT NULL,
      status TEXT NOT NULL
    );
  `);
};

export const saveMessage = async (message: VoiceMessage) => {
  if (!db) await initDB();
  // Ensure the file is in our document directory
  const fileName = message.filePath.split('/').pop() || 'recording.m4a';
  const newPath = (FileSystem.documentDirectory || '') + fileName;
  
  if (message.filePath !== newPath) {
    try {
        await FileSystem.copyAsync({
            from: message.filePath,
            to: newPath
        });
    } catch (e) {
        console.warn('File copy failed, using original path', e);
    }
  }

  await db?.runAsync(
    'INSERT OR REPLACE INTO messages (id, filePath, transcription, summary, createdAt, status) VALUES (?, ?, ?, ?, ?, ?)',
    message.id,
    newPath,
    message.transcription,
    message.summary,
    message.createdAt,
    message.status
  );
  return { ...message, filePath: newPath };
};

export const getMessages = async (): Promise<VoiceMessage[]> => {
  if (!db) await initDB();
  const allRows = await db?.getAllAsync('SELECT * FROM messages ORDER BY createdAt DESC');
  return (allRows as VoiceMessage[]) || [];
};

export const getMessageById = async (id: string): Promise<VoiceMessage | null> => {
  if (!db) await initDB();
  const row = await db?.getFirstAsync('SELECT * FROM messages WHERE id = ?', id);
  return (row as VoiceMessage) || null;
};

export const deleteMessage = async (id: string) => {
  if (!db) await initDB();
  await db?.runAsync('DELETE FROM messages WHERE id = ?', id);
};
