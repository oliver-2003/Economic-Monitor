-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema economic_monitor
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema economic_monitor
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `economic_monitor` DEFAULT CHARACTER SET utf8mb3 ;
USE `economic_monitor` ;

-- -----------------------------------------------------
-- Table `economic_monitor`.`bond_yields`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `economic_monitor`.`bond_yields` (
  `record_number` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `value` DECIMAL(10,4) NOT NULL,
  `record_date` DATE NOT NULL,
  `record_time` TIME NOT NULL,
  PRIMARY KEY (`record_number`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `economic_monitor`.`commodity_prices`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `economic_monitor`.`commodity_prices` (
  `record_number` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `value` DECIMAL(12,4) NOT NULL,
  `category` VARCHAR(100) NULL DEFAULT NULL,
  `record_date` DATE NULL DEFAULT NULL,
  `record_time` TIME NULL DEFAULT NULL,
  PRIMARY KEY (`record_number`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb`.`exchange_rates`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `economic_monitor`.`exchange_rates` (
  `record_number` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `value` DECIMAL(8,4) NOT NULL,
  `record_date` DATE NOT NULL,
  `record_time` TIME NOT NULL,
  PRIMARY KEY (`record_number`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb`.`market_indices`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `economic_monitor`.`market_indices` (
  `record_number` BIGINT NOT NULL AUTO_INCREMENT,
  `region_name` VARCHAR(45) NULL DEFAULT NULL,
  `name` VARCHAR(45) NOT NULL,
  `value` DECIMAL(12,4) NOT NULL,
  `close_value` DECIMAL(12,4) NULL DEFAULT NULL,
  `record_date` DATE NULL DEFAULT NULL,
  `record_time` TIME NULL DEFAULT NULL,
  PRIMARY KEY (`record_number`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `economic_monitor`.`stock_prices`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `economic_monitor`.`stock_prices` (
  `record_number` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `stock_exchange_name` VARCHAR(45) NULL DEFAULT NULL,
  `value` DECIMAL(10,3) NOT NULL,
  `open_price` DECIMAL(10,3) NULL DEFAULT NULL,
  `low_price` DECIMAL(10,3) NULL DEFAULT NULL,
  `high_price` DECIMAL(10,3) NULL DEFAULT NULL,
  `record_date` DATE NOT NULL,
  `record_time` TIME NOT NULL,
  PRIMARY KEY (`record_number`))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb3;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
