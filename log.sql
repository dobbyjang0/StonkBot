CREATE TABLE `log` (
  `index` int PRIMARY KEY AUTO_INCREMENT,
  `guild_id` int,
  `channel_id` int,
  `author_id` int,
  `stock_name` varchar(20)
);
