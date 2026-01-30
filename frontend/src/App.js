import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import Login from './Login';
import Dashboard from './Dashboard';

// --- INITIALIZE SUPABASE ---
const supabase = createClient(
  "https://qmnwjusineizolrpmcxq.supabase.co", 
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbndqdXNpbmVpem9scnBtY3hxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3ODIwMzEsImV4cCI6MjA2OTM1ODAzMX0.H4c-2fpB2a-UyB1RrnsQQjtvx8JXB94ps-C2KuF9vm4"
);

const App = () => {
  const [user, setUser] = useState(null);
  const [history, setHistory] = useState([]);

  // 1. Check if user is already logged in
  useEffect(() => {
    const session = localStorage.getItem('shelfie_user');
    if (session) {
      setUser(session);
      fetchHistory(session);
    }
  }, []);

  const fetchHistory = async (email) => {
    const { data } = await supabase
      .from('book_history')
      .select('*')
      .eq('user_email', email)
      .order('created_at', { ascending: false });
    setHistory(data || []);
  };

  const handleLogin = (email) => {
    setUser(email);
    localStorage.setItem('shelfie_user', email);
    fetchHistory(email);
  };

  const handleLogout = () => {
      setUser(null);
      localStorage.removeItem('shelfie_user');
  };

  const saveToHistory = async (analysisData, metadata, title) => {
      const { data, error } = await supabase.from('book_history').insert([{
          user_email: user,
          book_title: title,
          genre: analysisData.genre,
          summary: JSON.stringify(analysisData.summaries), // Storing all 3 summaries
          profanity_level: analysisData.profanity_level,
          reading_level: analysisData.vocab_level,
          word_count: metadata.word_count,
          read_time: metadata.read_time
      }]);
      fetchHistory(user); // Refresh list
  };

  return (
    <div className="App">
      {!user ? (
        <Login onLogin={handleLogin} />
      ) : (
        <Dashboard 
            user={user} 
            onLogout={handleLogout} 
            history={history} 
            onSave={saveToHistory}
        />
      )}
    </div>
  );
};

export default App;