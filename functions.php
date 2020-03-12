<?PHP
#AUTH HERE
if(!empty($_COOKIE['PHPSESSID']))
{
    session_start();
    if($_SESSION['REMOTE_ADDR'] != $_SERVER['REMOTE_ADDR'])
    {
        $_SESSION['AUTHED']=0;
        session_destroy();
        session_commit();
        header('Location: login.php');
        die('die');        
    }
    
    if($_SESSION['AUTHED']!=1)
    {
        $_SESSION['AUTHED']=0;
        session_destroy();
        session_commit();
        header('Location: login.php');
        die('die');
    }
}
else
{
    header('Location: login.php');
    die('die'); 
}

function listdir($dir, $root, $sep = '', $listed) {
    $rel_dir = substr($dir, strlen($root));

    if (!in_array($dir, $listed)) {
        $listed[] = $dir;
        echo "<option value=\"".$rel_dir."/\">".$rel_dir."/</option>";
    }

    $list = scandir($dir);
    if (is_array($list)) {
        $list = array_diff($list, array('.', '..'));
        if ($list) {
            foreach ($list as $name) {
                $path = $dir . '/' . $name;
                $rel_path = substr($path, strlen($root));
                $is_dir = is_dir($path);
                
                if ($is_dir) {
                    $listed[] = $path;
                    echo "<option value=\"".$rel_path."/\">".$sep.$rel_path."/</option>";
                }

                if ($is_dir) {
                    listdir($path, $root, $sep.'-', $listed);
                }
            }
        }
    } else
    {
        echo '<option>не могу прочитать</option>';
    }
}

function showdir($dir, $root, $showdir = 1, $showfiles = 1, $depth=1) {
    $list = scandir($root.$dir);
    if (is_array($list)) {
        $list = array_diff($list, array('.', '..'));
        if ($list) {
            
            $root_level=sizeof(explode('/',$root));
            $this_path_level=sizeof(explode('/',$root.$dir));
            $to_level=$this_path_level+$depth;
            $current_level=$this_path_level;
            echo '<ul style="list-style: none">';
            foreach ($list as $name) {
                $path = $root.$dir.'/'.$name;
                $rel_path = substr($path, strlen($root));
                $is_dir = is_dir($path);
                
                if ($is_dir) {
                    if ($showdir) {
                        echo '<li class="', $is_dir ? 'dir' : 'file', '">';
                        
                        
                        if ($current_level < $to_level) {
                            echo "<button class=\"mt-1 btn btn-outline-primary\" onclick=\"$(event.target).next().toggle(300);\">".htmlspecialchars($name)."</button>";
                            echo '<div class="dircontent">';
                            showdir($rel_path, $root, $showdir, $showfiles,($depth-1));
                            echo '</div>';
                        }
                        else
                        {
                            echo "<button class=\"mt-1 btn btn-outline-primary\" onclick=\"getDirContent('$rel_path', $(event.target).next()); $(event.target).next().toggle(300);\">".htmlspecialchars($name)."</button>";
                            echo '<div class="dircontent">';
                            echo 'loading dir content';
                            echo '</div>';                            
                        }
                        echo '</li>';
                    }
                } 
                else
                {
                    if ($showfiles) {
                        echo '<li class="', $is_dir ? 'dir' : 'file', '">';
                        echo '<div class="mt-1 border-bottom pb-1">
                        '.htmlspecialchars($name).'
                        <a class="btn btn-warning pt-0 pb-0" href="edit.php?file='.$rel_path.'">ИСХОДНИК</a>
                        <a class="btn btn-success pt-0 pb-0" href="wysiwyg.php?file='.$rel_path.'">ВИЗУАЛЬНО</a>
                        <a class="btn btn-primary pt-0 pb-0" href="'.$rel_path.'" target="_blank">перейти</a>
                        <a class="btn btn-info pt-0 pb-0" href="'.$rel_path.'" download="'.htmlspecialchars($name).'">скачать</a>
                        
                        </div>';
                        echo '</li>';
                    }
                }
            }
            echo '</ul>';
        }
    } else
    {
        echo '<i>не могу прочитать</i>
        <br> ROOT:'.$root.'
        <br>DIR: '.$dir;
    }
}

function getMySQLSettings() {
    $mysql_settings = [];
    if (file_exists(__DIR__.'/.mysql_settings')) {
        $mysqlset = file_get_contents(__DIR__.'/.mysql_settings');
        $mysql_settings = explode("\n", $mysqlset);
        /*
        структура файла настроек:
        хост
        база данных
        имя пользователя
        пароль
        */
    }
    return $mysql_settings;
}

function connectMySQL() {
    $mysql_settings = getMySQLSettings();
    if (!empty($mysql_settings[0])) {
        $CONN=mysqli_connect($mysql_settings[0], $mysql_settings[2], $mysql_settings[3], $mysql_settings[1]);
        if($CONN)
        {
            mysqli_query($CONN, "SET collation_connection = utf8mb4_general_ci");
            mysqli_query($CONN, "SET NAMES 'utf8' COLLATE 'utf8mb4_general_ci';");
            mysqli_set_charset($CONN,'utf8mb4');            
            return $CONN;
        }
        else
        {
            echo "MSQLCONERR: ".mysqli_connect_error();
            return false;
        }
        //return mysqli_connect('localhost', 'gov', 'gov', 'gov');
    }
    return '';
}

?>
