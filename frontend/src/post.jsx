import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PostForm from './PostForm'; // Import the form component

const Posts = () => {
    const [posts, setPosts] = useState([]);

    const fetchPosts = async () => {
        try {
            const result = await axios.get('/api/posts');
            if (Array.isArray(result.data)) {
                setPosts(result.data);
            } else {
                console.error('Received non-array response:', result.data);
                setPosts([]);
            }
        } catch (error) {
            console.error('Error fetching posts:', error);
            setPosts([]);
        }
    };

    useEffect(() => {
        fetchPosts();
    }, []);

    const handleNewPost = () => {
        fetchPosts(); // Refetch posts after a new post is created
    };

    return (
        <div>
            <PostForm onNewPost={handleNewPost} /> {/* Pass the refetch function as a prop */}
            {posts.map((post, index) => (
                <div key={index}>
                    <p>{post.content}</p>
                    <small>By: {post.author || 'Guest'}</small> {/* Display 'Guest' if no author is provided */}
                </div>
            ))}
        </div>
    );
};

export default Posts;
