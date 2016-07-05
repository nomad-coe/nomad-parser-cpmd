package eu.nomad_lab.parsers

import org.specs2.mutable.Specification

object CpmdParserSpec extends Specification {
  "test energy_force with json" >> {
    ParserRun.parse(CpmdParser, "parsers/cpmd/test/examples/single_point/output.out", "json") must_== ParseResult.ParseSuccess
  }
}
