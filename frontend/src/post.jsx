import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PostForm from './PostForm'; // Import the form component\
import "./post.css";

const Posts = () => {
    const [posts, setPosts] = useState([]);

    const fetchPosts = async () => {
        try {
            const result = await axios.get('/api/posts');
            console.log(result.data);
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

    const handlePostLike = async (postId) => {
        console.log("postId:", postId);
        try {
            const response = await axios.post(
                `/api/posts/${postId}/like`, 
                {},
                { withCredentials: true }
            );
            console.log("Post liked successfully:", response.data);
            fetchPosts();
        } catch (error) {
            console.error("Post like error:", error.response ? error.response.data : error);
        }
    };

    const handlePostComment = async (postId, comment) => {
        try {
            const response = await axios.post(
                `/api/posts/${postId}/comment`, 
                {comment},
                { withCredentials: true }
            );
            fetchPosts();
            console.log("Post comment successfully:", response.data);
        } catch (error) {
            console.error("Post comment error:", error.response ? error.response.data : error);
        }
    };
    

    return (
        <div>
            <PostForm onNewPost={handleNewPost} /> {/* Pass the refetch function as a prop */}
            {posts.map((post) => ( 
                <div key={post.post_id}>
                    <div className="post-header">
                    <img
                            src={post.author_profile_image || '/path/to/default/image.png'}
                            alt={`${post.author}'s profile`}
                            className="profile-pic"  // make sure you have the .profile-pic class in your CSS
                        />
                    <small>Post by: {post.author || 'Guest' }</small> {/* Display 'Guest' if no author is provided */}
                    </div>
                    <p>{post.content}</p>

                    <div>
                        <small>Likes: {post.like_count}</small>
                        <button onClick={() => handlePostLike(post.post_id)}>Like</button>
                    </div>
                    <CommentSection post={post} onAddComment ={handlePostComment} />
                </div>
            ))}
        </div>
    );
    
};

const CommentSection = ({post, onAddComment }) => {
    const [comment, setComment] = useState("");

    const addComment = (event) => {
        event.preventDefault();
        onAddComment (post.post_id, comment);
        setComment('');
    };

    
    
    return (
        <div>
            <form onSubmit={addComment}>
                <input
                    type="text"
                    placeholder="Add a comment"
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                />
                <button type="submit">Send comment</button>
            </form>

            <div>
                {post.comments && post.comments.map((comment, index) => (
                    <p key={index}>{comment.user}: {comment.comment}</p>
                ))}
            </div>

        </div>
    );
};

export default Posts;
