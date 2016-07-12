package eu.nomad_lab.parsers

import eu.{ nomad_lab => lab }
import eu.nomad_lab.DefaultPythonInterpreter
import org.{ json4s => jn }
import scala.collection.breakOut

object CpmdParser extends SimpleExternalParserGenerator(
  name = "CpmdParser",
  parserInfo = jn.JObject(
    ("name" -> jn.JString("CpmdParser")) ::
      ("parserId" -> jn.JString("CpmdParser" + lab.CpmdVersionInfo.version)) ::
      ("versionInfo" -> jn.JObject(
        ("nomadCoreVersion" -> jn.JObject(lab.NomadCoreVersionInfo.toMap.map {
          case (k, v) => k -> jn.JString(v.toString)
        }(breakOut): List[(String, jn.JString)])) ::
          (lab.CpmdVersionInfo.toMap.map {
            case (key, value) =>
              (key -> jn.JString(value.toString))
          }(breakOut): List[(String, jn.JString)])
      )) :: Nil
  ),
  mainFileTypes = Seq("text/.*"),
  mainFileRe = """               \*\*\*\*\*\*  \*\*\*\*\*\*    \*\*\*\*  \*\*\*\*  \*\*\*\*\*\*
              \*\*\*\*\*\*\*  \*\*\*\*\*\*\*   \*\*\*\*\*\*\*\*\*\*  \*\*\*\*\*\*\*
             \*\*\*       \*\*   \*\*\*  \*\* \*\*\*\* \*\*  \*\*   \*\*\*
             \*\*        \*\*   \*\*\*  \*\*  \*\*  \*\*  \*\*    \*\*
             \*\*        \*\*\*\*\*\*\*   \*\*      \*\*  \*\*    \*\*
             \*\*\*       \*\*\*\*\*\*    \*\*      \*\*  \*\*   \*\*\*
              \*\*\*\*\*\*\*  \*\*        \*\*      \*\*  \*\*\*\*\*\*\*
               \*\*\*\*\*\*  \*\*        \*\*      \*\*  \*\*\*\*\*\*
""".r,
  cmd = Seq(DefaultPythonInterpreter.pythonExe(), "${envDir}/parsers/cpmd/parser/parser-cpmd/cpmdparser/scalainterface.py",
    "${mainFilePath}"),
  cmdCwd = "${mainFilePath}/..",
  resList = Seq(
    "parser-cpmd/cpmdparser/__init__.py",
    "parser-cpmd/cpmdparser/setup_paths.py",
    "parser-cpmd/cpmdparser/parser.py",
    "parser-cpmd/cpmdparser/scalainterface.py",
    "parser-cpmd/cpmdparser/versions/__init__.py",
    "parser-cpmd/cpmdparser/versions/cpmd41/__init__.py",
    "parser-cpmd/cpmdparser/versions/cpmd41/mainparser.py",
    "parser-cpmd/cpmdparser/versions/cpmd41/inputparser.py",
    "parser-cpmd/cpmdparser/versions/cpmd41/commonparser.py",
    "parser-cpmd/cpmdparser/versions/cpmd41/input_data/cpmd_input_tree.pickle",
    "parser-cpmd/cpmdparser/generic/__init__.py",
    "parser-cpmd/cpmdparser/generic/inputparsing.py",
    "parser-cpmd/cpmdparser/tools/__init__.py",
    "parser-cpmd/cpmdparser/generic/inputparsing.py",
    "nomad_meta_info/public.nomadmetainfo.json",
    "nomad_meta_info/common.nomadmetainfo.json",
    "nomad_meta_info/meta_types.nomadmetainfo.json",
    "nomad_meta_info/cpmd.nomadmetainfo.json"
  ) ++ DefaultPythonInterpreter.commonFiles(),
  dirMap = Map(
    "parser-cpmd" -> "parsers/cpmd/parser/parser-cpmd",
    "nomad_meta_info" -> "nomad-meta-info/meta_info/nomad_meta_info"
  ) ++ DefaultPythonInterpreter.commonDirMapping()
)
