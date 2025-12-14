<?
define("SOCKET_STATUS_CONNECTED", 1); //新建立的连接
define("SOCKET_STATUS_NULLED", 2); //处理过NULL探针
define("SOCKET_STATUS_RECONNECTED", 3); //复用NULL探针连接之后重新创建的连接

/*
$taskResult = array();
$params = array();
$params["hostList"] = "124.70.138.134";
$params["portList"] = "1-1000";
execute($taskResult, $params);
*/
function execute($taskID, $params)
{
    $serviceList = array();
    @session_start();
    $_SESSION[$taskID]["running"] = "true";
    $_SESSION[$taskID]["result"] = json_encode($serviceList);
    @session_write_close();
    /**
     * 入参：hostList 主机IP地址列表，逗号分割
     * portList 待扫描端口列表，逗号分割，短横可标识范围
     */
    $hostList = $params["hostList"];
    $portList = $params["portList"];
    //$portList = "7-100";
    $probeFilePath = $params["probeFilePath"];
    $probeArr = json_decode(file_get_contents($probeFilePath), true);
    $hosts = parseHostList($hostList);
    $ports = parsePortList($portList);
    $timeout = 6;
    $status = array();
    $sockets = array();
    /* Initiate connections to all the hosts simultaneously */

    foreach ($hosts as $hostId => $host) {
        foreach ($ports as $portId => $port) {
            /*@session_start();
            $_SESSION[$taskID]["result"] ="[{\"id\":\"".$port."\"}]";
            @session_write_close();
            $sockObj = getSocket("tcp", "10.211.50.2", "80");
            sleep(1);*/
            foreach ($probeArr as $probeId => $probe) {
                //var_dump($probe);
                $challenge = $probe["challenge"];
                $matches = $probe["matches"];
                $type = strtolower($probe["type"]);
                $sockObj = getSocket($type, $host, $port);
                if ($sockObj == null || $sockObj["s_type"] == "error"||$sockObj["s"]==null) {
                    break;
                }
                $s_type = $sockObj["s_type"];
                $sock = $sockObj["s"];
                stream_set_timeout($sock, 3);
                $socketRead = "socket_read";
                $socketWrite = "socket_write";
                $socketClose = "socket_close";
                $socketSelect = "socket_select";
                if ($s_type == 'stream') {
                    $socketRead = "fread";
                    $socketWrite = "fwrite";
                    $socketClose = "fclose";
                    $socketSelect = "stream_select";
                }
                //echo $sock;
                if (strlen($challenge) > 0) {
                    $socketWrite($sock, warpChallenge($challenge));
                }
                $data = "";
                while (strlen($buf = $socketRead($sock, 8192)) > 0) {
                    $data = $data . $buf;
                }
                if (strlen($data) > 0) {
                    $service = doMatch($data, $matches);
                    $service["host"] = $host;
                    $service["port"] = $port;
                    $service["type"] = $type;
                    if (isset($service["service"])) {
                        foreach ($serviceList as $serviceId => $oldService)  //前面探针识别为unknown，后面探针需要进行更新
                        {
                            if ($oldService["host"] == $host && $oldService["port"] == $port && $oldService["service"] == "unknown") {
                                unset($serviceList[$serviceId]);
                                break;
                            }
                        }
                        array_push($serviceList, encodeArray($service));
                        saveResult($taskID, $serviceList);
                        break; //直接进入下一端口
                    } else {
                        $service["service"] = "unknown";
                        array_push($serviceList,encodeArray($service));
                        saveResult($taskID, $serviceList);
                    }
                }
            }
        }
    }
    @session_start();
    $_SESSION[$taskID]["running"] = "false";
    @session_write_close();
}
function saveResult($taskID, $result)
{
    @session_start();
    $_SESSION[$taskID]["result"] ="ffffff";
    $_SESSION[$taskID]["result"] = json_encode($result);
    @session_write_close();
}
function parseHostList($hostList)
{
    $hosts = explode(",", $hostList);
    return $hosts;
}
function parsePortList($portList)
{
    $ports = explode(",", $portList);
    foreach ($ports as $id => $port) {
        if (strpos($port, "-") > 0) {
            $start = explode("-", $port)[0];
            $stop = explode("-", $port)[1];
            unset($ports[$id]);
            for (; $start <= $stop; $start++) {
                array_push($ports, $start);
            }
        }
    }
    return $ports;
}

function buildProbeIndexList($probeArr, $port)
{
    foreach ($probeArr as $id => $probe) {
        if (array_key_exists("ports", $probe) || array_key_exists("sslports", $probe)) {
            $ports = "," . $probe["ports"];
        }
        if (array_key_exists("sslports", $probe)) {
            $ports = "," . $probe["sslports"];
        }
        $ports = $ports . ",";
        $ports = parsePortList($ports);
        if (in_array($port, $ports)) {
            unset($probeArr[$id]);
            array_unshift($probeArr, $probe);
        }
    }
}

function getSocket($type, $ip, $port)
{
    $resultObj = array();
    if (($f = 'stream_socket_client') && is_callable($f)) {
        $s = $f("{$type}://{$ip}:{$port}", $errno, $errmsg, 2);
        /*if ($errno1 == 111 || $errno1 == 10061) {
            return null;
        }*/
        $s_type = 'stream';
    }
    if (!$s && ($f = 'fsockopen') && is_callable($f)) {
        $s = $f("{$type}://{$ip}",$port, $errno, $errmsg, 2);
        $s_type = 'stream';
    }
    /*if (!$s && ($f = 'socket_create') && is_callable($f)) {
        $s = $f(AF_INET, SOCK_STREAM, SOL_TCP);
        $res = @socket_connect($s, $ip, $port);
        if (!$res) {
            die();
        }
        $s_type = 'socket';
    }*/
    if (!$s_type) {
        $s_type = "error";
        $s = 'no socket funcs';
    }
    if (!$s) {
        $s_type = "error";
        $s = 'no socket';
    }
    $resultObj["s"] = $s;
    $resultObj["s_type"] = $s_type;
    return $resultObj;
}

function warpChallenge($challenge)
{
    $challenge = str_replace("\\r", "\r", $challenge);
    $challenge = str_replace("\\n", "\n", $challenge);
    $challenge = unpack("C*", $challenge);
    //$challenge = array_map(fn ($value): string => chr($value), $challenge);
    $challenge = array_map(function ($value) {
        return chr($value);
    }, $challenge);
    $challenge = join("", $challenge);
    return $challenge;
}

function doMatch($data, $matches)
{
    $service = array();
    $service["banner"] = $data;
    foreach ($matches as $match) {
        $regex = $match["regex"];
        $regex = str_replace("/", "\/", $regex);
        $regex = "/" . $regex . "/";
        $option = $match["option"];
        if (strlen($option) > 0) {
            $regex = $regex . $option;
        }
        //echo "regex:".$regex."\nend";
        if (preg_match($regex, $data)) {
            $service["service"] = $match["service"];
            break;
        }
    }
    return $service;
}

function encodeArray($array)
{
    foreach($array as $key=>$value)
    {
        $array[$key]=base64_encode($value);
    }
    return $array;
}

