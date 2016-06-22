package eu.nomad_lab.parsers

import eu.{ nomad_lab => lab }
import eu.nomad_lab.DefaultPythonInterpreter
import org.{ json4s => jn }
import scala.collection.breakOut

object Cp2kParser extends SimpleExternalParserGenerator(
  name = "Cp2kParser",
  parserInfo = jn.JObject(
    ("name" -> jn.JString("CpmdParser")) ::
      ("parserId" -> jn.JString("CpmdParser" + lab.Cp2kVersionInfo.version)) ::
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
  mainFileRe = """  \*\*\*\* \*\*\*\* \*\*\*\*\*\*  \*\*  PROGRAM STARTED AT\s(?<cpmdStartedAt>.*)
 \*\*\*\*\* \*\* \*\*\*  \*\*\* \*\*   PROGRAM STARTED ON\s*.*
 \*\*    \*\*\*\*   \*\*\*\*\*\*    PROGRAM STARTED BY .*
 \*\*\*\*\* \*\*    \*\* \*\* \*\*   PROGRAM PROCESS ID .*
  \*\*\*\* \*\*  \*\*\*\*\*\*\*  \*\*  PROGRAM STARTED IN .*
(?:\s*\n|                                      \s+.*
)*
(?:\s*CP2K\| version string:\s*(?<cpmdVersionString>.*)
)?(?:\s*CP2K\| source code revision number:\s*(?<cpmdRevision>.*)
)?""".r,
  cmd = Seq(DefaultPythonInterpreter.python2Exe(), "${envDir}/parsers/cpmd/parser/parser-cpmd/cpmdparser/scalainterface.py",
    "${mainFilePath}"),
  cmdCwd = "${mainFilePath}/..",
  resList = Seq(
    "parser-cpmd/cpmdparser/__init__.py",
    "parser-cpmd/cpmdparser/setup_paths.py",
    "parser-cpmd/cpmdparser/parser.py",
    "parser-cpmd/cpmdparser/generic/__init__.py",
    "parser-cpmd/cpmdparser/versions/__init__.py",
    "parser-cpmd/cpmdparser/versions/versionsetup.py",
    "parser-cpmd/cpmdparser/versions/cpmd41/__init__.py",
    "parser-cpmd/cpmdparser/scalainterface.py",
    "nomad_meta_info/public.nomadmetainfo.json",
    "nomad_meta_info/common.nomadmetainfo.json",
    "nomad_meta_info/meta_types.nomadmetainfo.json",
    "nomad_meta_info/cpmd.nomadmetainfo.json",
    "nomad_meta_info/cpmd.general.nomadmetainfo.json"
  ) ++ DefaultPythonInterpreter.commonFiles(),
  dirMap = Map(
    "parser-cpmd" -> "parsers/cpmd/parser/parser-cpmd",
    "nomad_meta_info" -> "nomad-meta-info/meta_info/nomad_meta_info"
  ) ++ DefaultPythonInterpreter.commonDirMapping()
)
