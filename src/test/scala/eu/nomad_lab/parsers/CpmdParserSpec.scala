package eu.nomad_lab.parsers

import org.specs2.mutable.Specification

object CpmdParserSpec extends Specification {
  "CpmdParserTest" >> {
    "test with json-events" >> {
      ParserRun.parse(CpmdParser, "parsers/cpmd/test/examples/energy_force/si_bulk8.out", "json-events") must_== ParseResult.ParseSuccess
    }
  }

  "test energy_force with json" >> {
    ParserRun.parse(CpmdParser, "parsers/cpmd/test/examples/energy_force/si_bulk8.out", "json") must_== ParseResult.ParseSuccess
  }
}
