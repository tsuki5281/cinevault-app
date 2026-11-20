
-- Watched movies tracking
CREATE TABLE IF NOT EXISTS watched_movies (
    user_id INT NOT NULL,
    movie_id VARCHAR(10) NOT NULL,
    watched_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, movie_id),

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);
