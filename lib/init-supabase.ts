import { supabase } from './supabase';

export async function initSupabaseTables() {
  try {
    // Insert sample data if table is empty
    const { data: existingData, error: checkError } = await supabase
      .from('mock_chat_sessions')
      .select('id')
      .limit(1);

    if (checkError) {
      console.error('Error checking mock_chat_sessions:', checkError);
      return;
    }

    if (!existingData?.length) {
      const { error: insertError } = await supabase
        .from('mock_chat_sessions')
        .insert([
          {
            employee_id: '12345',
            status: 'active',
          }
        ]);

      if (insertError) {
        console.error('Error inserting sample chat session:', insertError);
        return;
      }

      console.log('Sample chat session data inserted successfully');
    }

    console.log('Supabase initialization completed');
  } catch (error) {
    console.error('Error during Supabase initialization:', error);
  }
} 