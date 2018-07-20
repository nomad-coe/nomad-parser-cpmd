/*
 * Copyright 2016-2018 Lauri Himanen, Fawzi Mohamed, Ankit Kariryaa
 * 
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

package eu.nomad_lab.parsers

import org.specs2.mutable.Specification

object CpmdParserSpec extends Specification {
  "CpmdParserTest" >> {
    "test with json-events" >> {
      ParserRun.parse(CpmdParser, "parsers/cpmd/test/examples/single_point/output.out", "json-events") must_== ParseResult.ParseSuccess
    }
  }

  "test energy_force with json" >> {
    ParserRun.parse(CpmdParser, "parsers/cpmd/test/examples/single_point/output.out", "json") must_== ParseResult.ParseSuccess
  }
  "test geo_opt with json" >> {
    ParserRun.parse(CpmdParser, "parsers/cpmd/test/examples/geo_opt/output.out", "json") must_== ParseResult.ParseSuccess
  }
  "test md with json" >> {
    ParserRun.parse(CpmdParser, "parsers/cpmd/test/examples/md/output.out", "json") must_== ParseResult.ParseSuccess
  }
}
