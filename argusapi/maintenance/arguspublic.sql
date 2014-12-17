-- MySQL dump 10.13  Distrib 5.5.24, for osx10.7 (i386)
--
-- Host: localhost    Database: argusdeltares
-- ------------------------------------------------------
-- Server version	5.5.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `IP`
--

DROP TABLE IF EXISTS `IP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `IP` (
  `seq` int(11) NOT NULL,
  `id` char(12) NOT NULL,
  `make` char(32) NOT NULL,
  `model` char(32) NOT NULL,
  `name` char(128) NOT NULL,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `IPidx` (`id`),
  UNIQUE KEY `IPseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `UTM`
--

DROP TABLE IF EXISTS `UTM`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `UTM` (
  `seq` int(11) NOT NULL,
  `id` char(5) NOT NULL,
  `lat` double NOT NULL,
  `lon` double NOT NULL,
  `elev` double NOT NULL,
  `zDatumNote` char(32) NOT NULL,
  `WGS84Height` double NOT NULL,
  `scaleCorrE` double NOT NULL,
  `scaleCorrN` double NOT NULL,
  `degFromN` double NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `UTMidx` (`id`),
  UNIQUE KEY `UTMseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `autoGeom`
--

DROP TABLE IF EXISTS `autoGeom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `autoGeom` (
  `seq` int(11) NOT NULL,
  `geometrySequence` int(11) NOT NULL,
  `cameraID` char(7) NOT NULL DEFAULT '',
  `IPID` char(8) NOT NULL,
  `dtilt` double NOT NULL,
  `dazimuth` double NOT NULL,
  `dfov` double NOT NULL,
  `droll` double NOT NULL,
  `tiltCI` double NOT NULL,
  `azimuthCI` double NOT NULL,
  `fovCI` double NOT NULL,
  `rollCI` double NOT NULL,
  `imagePath` char(128) NOT NULL,
  `whenDone` int(11) NOT NULL,
  `whenValid` int(11) NOT NULL,
  `usedDistortion` int(11) NOT NULL,
  `version` double NOT NULL,
  `protected` int(11) NOT NULL,
  `meanCorr` double NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `autoGeomseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `baseGeometry`
--

DROP TABLE IF EXISTS `baseGeometry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `baseGeometry` (
  `seq` int(11) NOT NULL,
  `cameraID` char(7) NOT NULL,
  `valid` int(11) NOT NULL,
  `m` blob NOT NULL,
  `R` blob NOT NULL,
  `tilt` double NOT NULL,
  `azimuth` double NOT NULL,
  `fov` double NOT NULL,
  `roll` double NOT NULL,
  `imagePath` char(128) NOT NULL,
  `whenDone` int(11) NOT NULL,
  `whenValid` int(11) NOT NULL,
  `user` char(16) NOT NULL DEFAULT '',
  `version` double NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `bgeomseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `baseUsedGCP`
--

DROP TABLE IF EXISTS `baseUsedGCP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `baseUsedGCP` (
  `seq` int(11) NOT NULL,
  `gcpID` char(8) NOT NULL,
  `baseGeometrySeq` int(11) NOT NULL,
  `U` double NOT NULL,
  `V` double NOT NULL,
  `PPP` int(11) NOT NULL,
  `eccentricity` double NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `bugcpseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `camera`
--

DROP TABLE IF EXISTS `camera`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `camera` (
  `seq` int(11) NOT NULL,
  `id` char(7) NOT NULL,
  `stationID` char(7) NOT NULL,
  `modelID` char(5) NOT NULL,
  `syncsToID` char(7) NOT NULL,
  `lensModelID` char(5) NOT NULL,
  `lensSN` char(16) NOT NULL,
  `cameraSN` char(16) NOT NULL,
  `polarizer` int(11) NOT NULL,
  `polAngle` double DEFAULT NULL,
  `filters` char(32) NOT NULL,
  `orientation` char(6) NOT NULL,
  `cameraNumber` int(11) NOT NULL,
  `kramerButton` int(11) NOT NULL,
  `timeIN` int(11) NOT NULL,
  `timeOUT` int(11) NOT NULL,
  `x` double NOT NULL,
  `y` double NOT NULL,
  `z` double NOT NULL,
  `D1` double NOT NULL,
  `D2` double NOT NULL,
  `Destimated` int(11) NOT NULL,
  `K` tinyblob NOT NULL,
  `Drad` tinyblob NOT NULL,
  `Dtan` tinyblob NOT NULL,
  `D_U0` double NOT NULL,
  `D_V0` double NOT NULL,
  `IPID` char(12) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `cameraidx` (`id`),
  UNIQUE KEY `cameraseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cameraModel`
--

DROP TABLE IF EXISTS `cameraModel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cameraModel` (
  `seq` int(11) NOT NULL,
  `id` char(5) NOT NULL,
  `make` char(32) NOT NULL,
  `model` char(32) NOT NULL,
  `size` double NOT NULL,
  `color` int(11) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `cameraModelidx` (`id`),
  UNIQUE KEY `cameraModelseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dbdefs`
--

DROP TABLE IF EXISTS `dbdefs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dbdefs` (
  `tableName` char(16) DEFAULT NULL,
  `fieldName` char(32) DEFAULT NULL,
  `fieldType` char(8) DEFAULT NULL,
  `fieldLength` int(11) DEFAULT NULL,
  `meaning` char(60) DEFAULT NULL,
  `timestamp` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `eurobuoy`
--

DROP TABLE IF EXISTS `eurobuoy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eurobuoy` (
  `seq` int(11) NOT NULL,
  `id` char(255) NOT NULL,
  `projection` char(64) NOT NULL,
  `easting` double DEFAULT NULL,
  `northing` double DEFAULT NULL,
  `timestamp` int(11) NOT NULL,
  UNIQUE KEY `ebseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `eurodata`
--

DROP TABLE IF EXISTS `eurodata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eurodata` (
  `seq` int(11) NOT NULL,
  `param` char(16) NOT NULL,
  `unit` double NOT NULL,
  `col` int(11) NOT NULL,
  `pref` int(11) NOT NULL,
  `parent` char(32) NOT NULL,
  `parentSeq` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  UNIQUE KEY `euseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `eurofielddata`
--

DROP TABLE IF EXISTS `eurofielddata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eurofielddata` (
  `seq` int(11) NOT NULL,
  `siteID` char(7) NOT NULL,
  `fname` varchar(950) NOT NULL DEFAULT '',
  `source` char(255) NOT NULL,
  `buoyID` char(255) NOT NULL,
  `timeIN` int(11) NOT NULL,
  `timeOUT` int(11) NOT NULL,
  `dt` int(11) NOT NULL,
  `ls_eurodata` char(64) NOT NULL,
  `error` char(8) NOT NULL,
  `datagap` int(11) NOT NULL,
  `accessCall` char(64) NOT NULL,
  `timestamp` int(11) NOT NULL,
  UNIQUE KEY `euwseq` (`seq`),
  UNIQUE KEY `fieldfname` (`fname`,`siteID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `eurointertidal`
--

DROP TABLE IF EXISTS `eurointertidal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eurointertidal` (
  `seq` int(11) NOT NULL,
  `siteID` char(7) NOT NULL,
  `fname` varchar(950) NOT NULL DEFAULT '',
  `source` char(64) NOT NULL,
  `intertidalModel` char(64) NOT NULL,
  `whenValid` int(11) NOT NULL,
  `error` char(8) NOT NULL,
  `refLevel` char(32) NOT NULL,
  `projection` char(64) NOT NULL,
  `timestamp` int(11) NOT NULL,
  UNIQUE KEY `euinseq` (`seq`),
  UNIQUE KEY `inttidfname` (`fname`,`siteID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `euromet`
--

DROP TABLE IF EXISTS `euromet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `euromet` (
  `seq` int(11) NOT NULL,
  `siteID` char(7) NOT NULL,
  `fname` varchar(950) NOT NULL DEFAULT '',
  `source` char(255) NOT NULL,
  `buoyID` char(255) NOT NULL,
  `timeIN` int(11) NOT NULL,
  `timeOUT` int(11) NOT NULL,
  `dt` int(11) NOT NULL,
  `ls_eurodata` char(64) NOT NULL,
  `error` char(8) NOT NULL,
  `datagap` int(11) NOT NULL,
  `accessCall` char(64) NOT NULL,
  `timestamp` int(11) NOT NULL,
  UNIQUE KEY `euwseq` (`seq`),
  UNIQUE KEY `metfname` (`fname`,`siteID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `euromorph`
--

DROP TABLE IF EXISTS `euromorph`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `euromorph` (
  `seq` int(11) NOT NULL,
  `siteID` char(7) NOT NULL,
  `fname` varchar(950) NOT NULL DEFAULT '',
  `source` char(64) NOT NULL,
  `whenValid` int(11) NOT NULL,
  `error` char(8) NOT NULL,
  `refLevel` char(32) NOT NULL,
  `projection` char(64) NOT NULL,
  `timestamp` int(11) NOT NULL,
  UNIQUE KEY `eumseq` (`seq`),
  UNIQUE KEY `morphfname` (`fname`,`siteID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `eurotide`
--

DROP TABLE IF EXISTS `eurotide`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eurotide` (
  `seq` int(11) NOT NULL,
  `siteID` char(7) NOT NULL,
  `fname` varchar(950) NOT NULL DEFAULT '',
  `source` char(255) NOT NULL,
  `buoyID` char(255) NOT NULL,
  `timeIN` int(11) NOT NULL,
  `timeOUT` int(11) NOT NULL,
  `dt` int(11) NOT NULL,
  `ls_eurodata` char(64) NOT NULL,
  `error` char(8) NOT NULL,
  `datagap` int(11) NOT NULL,
  `refLevel` char(32) NOT NULL,
  `accessCall` char(64) NOT NULL,
  `timestamp` int(11) NOT NULL,
  UNIQUE KEY `euwseq` (`seq`),
  UNIQUE KEY `tidefname` (`fname`,`siteID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `eurowave`
--

DROP TABLE IF EXISTS `eurowave`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eurowave` (
  `seq` int(11) NOT NULL,
  `siteID` char(7) NOT NULL,
  `fname` varchar(950) NOT NULL DEFAULT '',
  `source` char(255) NOT NULL,
  `buoyID` char(255) NOT NULL,
  `timeIN` int(11) NOT NULL,
  `timeOUT` int(11) NOT NULL,
  `dt` int(11) NOT NULL,
  `ls_eurodata` char(64) NOT NULL,
  `error` char(8) NOT NULL,
  `datagap` int(11) NOT NULL,
  `accessCall` char(64) NOT NULL,
  `timestamp` int(11) NOT NULL,
  UNIQUE KEY `euwseq` (`seq`),
  UNIQUE KEY `wavefname` (`fname`,`siteID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gcp`
--

DROP TABLE IF EXISTS `gcp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gcp` (
  `seq` int(11) NOT NULL,
  `id` char(8) NOT NULL,
  `name` char(128) NOT NULL,
  `siteID` char(7) NOT NULL,
  `timeIN` int(11) NOT NULL,
  `timeOUT` int(11) NOT NULL,
  `x` double NOT NULL,
  `y` double NOT NULL,
  `z` double NOT NULL,
  `xDim` double NOT NULL,
  `yDim` double NOT NULL,
  `intensity` int(11) NOT NULL,
  `eccentricity` double NOT NULL,
  `PPPable` int(11) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `gcpidx` (`id`),
  UNIQUE KEY `gcpseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `geometry`
--

DROP TABLE IF EXISTS `geometry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `geometry` (
  `seq` int(11) NOT NULL,
  `cameraID` char(7) NOT NULL,
  `valid` int(11) NOT NULL,
  `m` tinyblob NOT NULL,
  `tilt` double NOT NULL,
  `azimuth` double NOT NULL,
  `fov` double NOT NULL,
  `roll` double NOT NULL,
  `imagePath` char(64) NOT NULL,
  `whenDone` int(11) NOT NULL,
  `whenValid` int(11) NOT NULL,
  `usedDistortion` int(11) NOT NULL,
  `user` char(16) NOT NULL DEFAULT '',
  `usedHorizon` int(11) NOT NULL,
  `err` double NOT NULL,
  `iterations` int(11) NOT NULL,
  `version` double NOT NULL,
  `qual1` double NOT NULL,
  `qual2` double NOT NULL,
  `qual3` double NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `geomseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `keywords`
--

DROP TABLE IF EXISTS `keywords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `keywords` (
  `seq` int(11) NOT NULL,
  `path` char(255) NOT NULL,
  `words` char(64) NOT NULL,
  `comment` char(128) NOT NULL,
  `hrmC` int(11) NOT NULL,
  `internal` int(11) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `keyseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lensModel`
--

DROP TABLE IF EXISTS `lensModel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lensModel` (
  `seq` int(11) NOT NULL,
  `id` char(5) NOT NULL,
  `make` char(32) NOT NULL,
  `model` char(32) NOT NULL,
  `f` double NOT NULL,
  `aperture` double NOT NULL,
  `autoIris` int(11) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `lensModelidx` (`id`),
  UNIQUE KEY `lensModelseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sequence`
--

DROP TABLE IF EXISTS `sequence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sequence` (
  `seq` int(11) DEFAULT NULL,
  `IP` int(11) NOT NULL,
  `UTM` int(11) NOT NULL,
  `autoGeom` int(11) NOT NULL,
  `baseGeometry` int(11) NOT NULL,
  `baseUsedGCP` int(11) NOT NULL,
  `camera` int(11) NOT NULL,
  `cameraModel` int(11) NOT NULL,
  `dbdefs` int(11) NOT NULL,
  `eurobuoy` int(11) NOT NULL,
  `eurodata` int(11) NOT NULL,
  `eurofielddata` int(11) NOT NULL,
  `eurointertidal` int(11) NOT NULL,
  `euromet` int(11) NOT NULL,
  `euromorph` int(11) NOT NULL,
  `eurotide` int(11) NOT NULL,
  `eurowave` int(11) NOT NULL,
  `gcp` int(11) NOT NULL,
  `geometry` int(11) NOT NULL,
  `keywords` int(11) NOT NULL,
  `lensModel` int(11) NOT NULL,
  `site` int(11) NOT NULL,
  `station` int(11) NOT NULL,
  `template` int(11) NOT NULL,
  `usedGCP` int(11) NOT NULL,
  `usedTemplate` int(11) NOT NULL,
  `vettedBwEpochs` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `site`
--

DROP TABLE IF EXISTS `site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `site` (
  `seq` int(11) NOT NULL,
  `id` char(7) NOT NULL,
  `siteID` char(10) NOT NULL DEFAULT '',
  `name` char(64) NOT NULL,
  `lat` double NOT NULL,
  `lon` double NOT NULL,
  `elev` double NOT NULL,
  `zDatumNote` char(32) NOT NULL,
  `WGS84Height` double NOT NULL,
  `scaleCorrE` double NOT NULL,
  `scaleCorrN` double NOT NULL,
  `TZoffset` int(11) NOT NULL,
  `tideSource` char(64) NOT NULL,
  `waveSource` char(255) NOT NULL,
  `degFromN` double NOT NULL,
  `owner` char(20) NOT NULL,
  `TZName` char(8) NOT NULL,
  `useLocalNames` int(11) NOT NULL,
  `sortLocalTime` int(11) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  `coordinateOrigin` tinyblob,
  `coordinateRotation` double DEFAULT NULL,
  `coordinateEPSG` int(11) DEFAULT NULL,
  UNIQUE KEY `siteidx` (`id`),
  UNIQUE KEY `siteseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `station`
--

DROP TABLE IF EXISTS `station`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `station` (
  `seq` int(11) NOT NULL,
  `id` char(7) NOT NULL,
  `shortName` char(10) NOT NULL DEFAULT '',
  `name` char(64) NOT NULL,
  `siteID` char(7) NOT NULL,
  `timeIN` int(11) NOT NULL,
  `timeOUT` int(11) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `stationidx` (`id`),
  UNIQUE KEY `stationseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `template`
--

DROP TABLE IF EXISTS `template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `template` (
  `seq` int(11) NOT NULL,
  `id` char(8) NOT NULL,
  `name` char(32) NOT NULL,
  `imageName` char(128) NOT NULL,
  `usedGeometry` int(11) NOT NULL,
  `cameraID` char(8) NOT NULL,
  `whenDone` int(11) NOT NULL,
  `sunAzimuth` double NOT NULL,
  `sunAltitude` double NOT NULL,
  `Ncolumns` int(11) NOT NULL,
  `Nrows` int(11) NOT NULL,
  `fixVar` char(1) NOT NULL,
  `fixVal` double NOT NULL,
  `timeIN` int(11) NOT NULL,
  `timeOUT` int(11) NOT NULL,
  `U` longblob,
  `V` longblob,
  `R` longblob,
  `G` longblob,
  `B` longblob,
  `minSunAzimuth` longblob,
  `maxSunAzimuth` longblob,
  `minSunAltitude` longblob,
  `maxSunAltitude` longblob,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `tempseq` (`seq`),
  UNIQUE KEY `tempid` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usedGCP`
--

DROP TABLE IF EXISTS `usedGCP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usedGCP` (
  `seq` int(11) NOT NULL,
  `gcpID` char(8) NOT NULL,
  `geometrySequence` int(11) NOT NULL,
  `U` double NOT NULL,
  `V` double NOT NULL,
  `PPP` int(11) NOT NULL,
  `eccentricity` double NOT NULL,
  `templateID` char(6) NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `ugcpIdx` (`gcpID`,`geometrySequence`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usedTemplate`
--

DROP TABLE IF EXISTS `usedTemplate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usedTemplate` (
  `seq` int(11) NOT NULL,
  `templateID` char(8) NOT NULL,
  `autoGeomSequence` int(11) NOT NULL,
  `corr` double NOT NULL,
  `timestamp` int(11) DEFAULT NULL,
  UNIQUE KEY `utseq` (`seq`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-06-14 10:14:16
