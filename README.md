# cch

Cloud CLI for Humans

Very simple cloud CLI, specifically designed for human use. Strictly forbidden
for scripts' consumption :)

More information in my blog post ["A Different Approach to AWS CLI"](http://www.rushiagr.com/blog/2016/01/02/better-aws-command-line-interface/)

View demo at: https://asciinema.org/a/ektm98481nniu7rldc1ncu5af

# Installation

Simply run:

    $ pip install cch

You might need to configure AWS credentials if not configured in your system
already. Just run `aws configure` and provide access key, secret key and
region. This will keep credentials in your system in `~/.aws/config` and
`~/.aws/credentials` files.

# Usage

To use it:

    $ cch --help

# All commands

    lsvm    - List all virtual machines
    mkvm    - Create a virtual machine
    stpvm   - Stop a virtual machine
    rmvm    - Terminate a virtual machine

    lskp    - List all keypairs
    mkkp    - Create keypairs
    rmkp    - Delete a keypair

    lssg    - List all security groups (including a detailed view)
    mksg    - Create a security group (including specifying secgroup rules)
    rmsg    - Delete a security group

# Etc

* Look at `notes/plan` for a short list of things I had in my mind while developing this library
* Many edge-cases haven't been taken care of right now. Feel free to submit a pull request :)
