mehtrace
========

**mehtrace** is a system call tracer for amd64 Linux.

The name comes from the fact that it is mediocre, but kind of does the job.

The goal of this little project was to get an strace-like tool running with as
few build dependencies as possible.

I plan to provide a better write-up soon.

Build requirements
------------------

 * a C compiler in your `PATH` under the name `cc`

 * a Python 3.6+ interpreter in your `PATH`

 * a `curl` binary in your `PATH`

 * some internet access to fetch a 107 KiB JSON

   * The JSON contains a syscall signature list created by @FiloSottile
     as part of <https://filippo.io/linux-syscall-table/>
     (used here under the terms of the Unlicense as per
     <https://twitter.com/FiloSottile/status/1181977423358943238>).
     It's incredibly handy.


 * a `ninja` binary in your `PATH`

   * This might be a little shock to some, but I preferred to write a Ninja
     build file by hand over writing a Makefile by hand. And a `ninja` binary
     can be bootstrapped rather easily even on my uni lab system.

Big thanks to:
--------------

 * @FiloSottile for <https://filippo.io/linux-syscall-table/> and allowing me to
   use the JSON from it.

 * @sio2project/sio2jail authors for making my study of ptrace arts easier with
   their code.

 * My faculty's computer laboratory administrators for upgrading the systems
   from PLD Linux 3.0 to Debian 10. I'm not mad at the rough edges, and hey,
   I got to try out something nice in process.
