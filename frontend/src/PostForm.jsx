import React, { useState } from 'react';
import axios from 'axios';

const PostForm = ({ onNewPost }) => { 
    const [content, setContent] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            const response = await axios.post('/api/posts', { content }, { withCredentials: true });
            console.log('Post created:', response.data);
            setContent('');
            onNewPost(); 
        } catch (error) {
            console.error('Error creating post:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <textarea 
                value={content} 
                onChange={e => setContent(e.target.value)} 
                placeholder="What's on your mind?" 
                required 
            />
            <button type="submit">Create Post</button>
        </form>
    );
};

export default PostForm;
