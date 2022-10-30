<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">

<h1 align="center">Minimum Risk Portfolio Generator</h1>

  <p align="center">
    Feedback assisted quantum annealing for hedging in portfolio optimization
    <br />
    <a href="https://github.com/Ashish0z/portfolio_generator_QuantYantriki">View Demo</a>
    ·
    <a href="https://github.com/Ashish0z/portfolio_generator_QuantYantriki/issues">Report Bug</a>
    ·
    <a href="https://github.com/Ashish0z/portfolio_generator_QuantYantriki/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href=#contributors>Contributors</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![Usage][product-screenshot]

We propose a novel feedback assisted quantum annealing algorithm for hedging where the optimal portfolio at a future time can be obtained by incorporating information contained in the covariance matrix as well as from other sources such as simulations and machine learning algorithms. This can potentially make the use of quantum annealing for hedging more reliable and improve the balance optimality of asset allocation for a fixed future time.

The algorithm starts by using quantum annealing to find a probability distribution over optimal asset allocation vectors based only on the covariance matrix. A subset of the elements of the asset allocation vector is then randomly sampled and compared with the optimal portfolio at a future time - the latter obtained via alternate means described above. If the marginal probability of the sampled subset of assets lies above a user-defined threshold we accept the entire asset allocation vector as the optimal prediction for that time. In the other case, we repeat quantum annealing with the same covariance matrix as before but now with biasing (using local-fields on the annealer) on the sampled variables to set them to desired values. This process can be shown to converge in linear time which is when the algorithm stops and provides us with an optimal asset allocation vector at a fixed future time.

This project contains the program that implement the above approach using the Dwave Ocean SDK and IBM Qiskit along with a django based UI that allows you to select the inputs and call either of the subroutines to calculate the optimal porfolio. 


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![DWave Ocean SDK][dwavesys.com]][Dwave-url]
* [![IBM QISKIT][qiskit.org]][qiskit-url]
* [![Django][djangoproject.com]][Django-url]
* [![JQuery][JQuery.com]][JQuery-url]
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Python
  ```sh
  sudo apt install python3
  ```

### Installation

1. Create a virtual environment
   ```sh  
   python3 -m venv /path/to/new/virtual/environment

   source /path/to/new/virtual/environment/bin/activate
   ```
2. Clone the repo inside the virtual environment
   ```sh
   cd /path/to/new/virtual/environment
   git clone https://github.com/Ashish0z/portfolio_generator_QuantYantriki.git
   ```
3. Install required python modules
   ```sh
   cd /path/to/new/virtual/environment/portfolio_generator_QuantYantriki
   pip install -r requirements.txt
   ```

### Running the UI
1. Run Development Server
   ```sh
   python3 manage.py runserver
   ```
2. Open your browser and go to <a href = http://127.0.0.1/8000>http://127.0.0.1/8000</a>
<p align="right">(<a href="#readme-top">back to top</a>)</p>






<!-- CONTRIBUTING -->
## Contributors

This project was made by Team QuantYantriki for Quantum Science and Technology Hackathon 2022 
<br />
Team Member Details:
* Siddartha Santra
* Ashish Patel
* Shashwat Chakraborty
* Aneesh Kamat 

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Ashish0z/portfolio_generator_QuantYantriki.svg?style=for-the-badge
[contributors-url]: https://github.com/Ashish0z/portfolio_generator_QuantYantriki/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Ashish0z/portfolio_generator_QuantYantriki.svg?style=for-the-badge
[forks-url]: https://github.com/Ashish0z/portfolio_generator_QuantYantriki/network/members
[stars-shield]: https://img.shields.io/github/stars/Ashish0z/portfolio_generator_QuantYantriki.svg?style=for-the-badge
[stars-url]: https://github.com/Ashish0z/portfolio_generator_QuantYantriki/stargazers
[issues-shield]: https://img.shields.io/github/issues/Ashish0z/portfolio_generator_QuantYantriki.svg?style=for-the-badge
[issues-url]: https://github.com/Ashish0z/portfolio_generator_QuantYantriki/issues
[license-shield]: https://img.shields.io/github/license/Ashish0z/portfolio_generator_QuantYantriki.svg?style=for-the-badge
[license-url]: https://github.com/Ashish0z/portfolio_generator_QuantYantriki/blob/master/LICENSE.txt
[product-screenshot]: Examples/example.gif
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
[dwavesys.com]:https://shields.io/badge/-DWave%20Systems-008CD7?style=for-the-badge&logo=dwavesystems
[Dwave-url]:https://www.dwavesys.com
[qiskit.org]:https://shields.io/badge/-Qiskit-6929C4?style=for-the-badge&logo=qiskit
[qiskit-url]:https://www.qiskit.org
[djangoproject.com]:https://shields.io/badge/-Django-092E20?style=for-the-badge&logo=django
[Django-url]:https://www.djangoproject.com