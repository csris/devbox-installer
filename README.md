This repo contains a script meant to make it easier to install software on a new laptop. Ideally, though I haven't tried, I should just be able to `curl` this script from Github and run it with python3.

## Design
Because the script is meant to be `curl`'ed on a new laptop, there are a few restrictions on the design. First, it must all be in one file. If this proves too unwieldy, I might write a preprocessor in the future to concatenate multiple files together. Second, it cannot use any dependencies except for modules provided in the standard library.

The overall design of this script is inspired by [Prodspec and Annealing](https://www.usenix.org/publications/loginonline/prodspec-and-annealing-intent-based-actuation-google-production), which itself is inspired by [Entity Component System] architectures in game design—hence the somewhat odd naming in the script.

## License
```
   Copyright (c) 2023 Charles Srisuwananukorn

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
