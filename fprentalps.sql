-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 19, 2024 at 02:45 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fprentalps`
--

-- --------------------------------------------------------

--
-- Table structure for table `device`
--

CREATE TABLE `device` (
  `id_device` int(10) NOT NULL,
  `device` enum('PS3','PS4','PS5') NOT NULL,
  `harga` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `device`
--

INSERT INTO `device` (`id_device`, `device`, `harga`) VALUES
(1, 'PS3', 75000),
(2, 'PS4', 100000),
(3, 'PS5', 150000);

-- --------------------------------------------------------

--
-- Table structure for table `sewa`
--

CREATE TABLE `sewa` (
  `id_sewa` int(15) NOT NULL,
  `tanggal_sewa` date NOT NULL,
  `tanggal_kembali` date NOT NULL,
  `total_harga` int(10) NOT NULL,
  `device_id` int(10) NOT NULL,
  `user_id` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sewa`
--

INSERT INTO `sewa` (`id_sewa`, `tanggal_sewa`, `tanggal_kembali`, `total_harga`, `device_id`, `user_id`) VALUES
(3, '2024-06-27', '2024-06-28', 50000, 3, 2),
(16, '2024-06-30', '2024-07-03', 450000, 3, 6),
(18, '2024-07-04', '2024-07-08', 400000, 2, 11),
(19, '2024-07-03', '2024-07-04', 150000, 3, 11),
(20, '2024-07-01', '2024-07-06', 750000, 3, 7),
(21, '2024-07-01', '2024-07-04', 300000, 2, 2),
(23, '2024-07-01', '2024-07-02', 75000, 1, 2),
(25, '2024-07-01', '2024-07-04', 450000, 3, 6),
(28, '2024-11-24', '2024-12-01', 1050000, 3, 7),
(29, '2024-12-13', '2024-12-16', 300000, 2, 13),
(30, '2024-12-13', '2024-12-15', 150000, 1, 13),
(31, '2024-12-19', '2024-12-27', 800000, 2, 6);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(10) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `nama` varchar(50) NOT NULL,
  `no_hp` varchar(12) NOT NULL,
  `alamat` varchar(100) NOT NULL,
  `role` enum('admin','member') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `nama`, `no_hp`, `alamat`, `role`) VALUES
(1, 'aking', 'password123', 'Krisna', '08123456789', 'Concat', 'admin'),
(2, 'Bedul', 'memberpass', 'Abdullah Azzam Azed', '08234567890', 'Wonosobo', 'member'),
(6, 'Asep', '456', 'M. Hisyam Ramadhan', '081234567890', 'Gejayan', 'member'),
(7, 'krist00n', '123', 'Faesal Krisna Wijaya', '087654321', 'Purworejo', 'member'),
(11, 'Gupolo', '123', 'Gilang Wahyu Pratama', '00986645634', 'Pingit', 'member'),
(13, 'lilhadar', 'hadar123', 'Hadar', '08123456789', 'Nganjuk', 'member'),
(14, 'galih', '12345', 'king repel', '089089893843', 'kotagede', 'member'),
(15, 'R', 'kntl', 'Rafli', '085555555', 'Bangkok', 'member');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `device`
--
ALTER TABLE `device`
  ADD PRIMARY KEY (`id_device`);

--
-- Indexes for table `sewa`
--
ALTER TABLE `sewa`
  ADD PRIMARY KEY (`id_sewa`),
  ADD KEY `device_id` (`device_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `device`
--
ALTER TABLE `device`
  MODIFY `id_device` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `sewa`
--
ALTER TABLE `sewa`
  MODIFY `id_sewa` int(15) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `sewa`
--
ALTER TABLE `sewa`
  ADD CONSTRAINT `sewa_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `device` (`id_device`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `sewa_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
