# This file is run on a plain virgin Linux VM and only requires puppet and git to be installed

class code {
    vcsrepo {'/home/bbr/bbr4':
        ensure => latest,
        provider => git,
        source => 'https://github.com/BrassBandResults/bbr4.git',
        user => 'bbr',
    }
}

include code